"""Private, no-LLM news reader. Python 3.12+, standard library only."""
import argparse
import gzip
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

AIHOT = 'https://aihot.news/api/v1/dailies/latest'
CHINA = ZoneInfo('Asia/Shanghai')
MAX_BYTES = 2_000_000

class SafeError(Exception):
    """Only fixed, non-sensitive messages may cross the logging boundary."""

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SafeError('推送端点发生重定向，已停止；请核对官方文档。')


def read_response(response):
    data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise SafeError('来源响应过大。')
    if response.headers.get('Content-Encoding') == 'gzip':
        # Bound decompressed data as well.
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise SafeError('来源解压响应过大。')
    return data


def get(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': 'private-morning-briefing/1.0', 'Accept-Encoding': 'gzip'})
    # One daily GET, no automatic retries/rate-limit bypass.
    with urllib.request.urlopen(request, timeout=30) as response:
        return read_response(response)


def plain(value, limit=220):
    text = re.sub('<[^>]*>', '', html.unescape(str(value or '')))
    text = re.sub(r'\s+', ' ', text).strip()
    text = text[:limit] + ('…' if len(text) > limit else '')
    return re.sub(r'([\\`*{}\[\]<>#|])', r'\\\1', text)


def safe_url(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return ''
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        return ''
    return value.replace('(', '%28').replace(')', '%29')


def parse_ai(payload, now):
    if payload.get('schemaVersion') != 1:
        raise SafeError('AIHOT 接口版本变化，需更新解析器。')
    report = payload.get('report') or {}
    if report.get('date') != now.astimezone(CHINA).date().isoformat():
        raise SafeError('AIHOT 今日日报尚未就绪；未把旧日报作为今天的新闻发送。')
    items = []
    seen = set()
    for section in report.get('sections', []):
        for raw in section.get('items', []):
            links = raw.get('links') or {}
            original = safe_url(links.get('original'))
            canonical = safe_url((raw.get('attribution') or {}).get('url')) or safe_url(links.get('aihot'))
            title = raw.get('title')
            if not title or not original or not canonical or original in seen:
                continue
            seen.add(original)
            items.append({'title': title, 'summary': raw.get('summary', ''),
                          'url': original, 'canonical': canonical,
                          'source': (raw.get('source') or {}).get('name', '原始来源'),
                          'category': section.get('label', '')})
    for raw in report.get('flashes', []):
        links = raw.get('links') or {}
        original = safe_url(links.get('original'))
        canonical = safe_url((raw.get('attribution') or {}).get('url')) or safe_url(links.get('aihot'))
        if raw.get('title') and original and canonical and original not in seen:
            seen.add(original)
            items.append({'title': raw['title'], 'summary': '', 'url': original,
                          'canonical': canonical, 'source': (raw.get('source') or {}).get('name', '原始来源'),
                          'category': '快讯'})
    return items[:20]


def render(ai, notices, now):
    date = now.astimezone(CHINA).date().isoformat()
    lines = [f'# AIHOT 日报 · {date}',
        'AIHOT 内容摘编：保留标题、短摘要、原始来源和 AIHOT 归属链接。没有另行调用大模型，也未独立核验每条原始报道。',
        f'生成时间：{now.astimezone(CHINA):%Y-%m-%d %H:%M}（北京时间）',
        f'[阅读 AIHOT 完整日报](https://aihot.news/daily/{date})']
    for notice in notices:
        lines += [f'提示：{notice}']
    category = None
    for item in ai:
        if item['category'] != category:
            category = item['category']
            lines += [f'## {plain(category, 60)}']
        lines += [f'### {plain(item["title"])}']
        if item['summary']:
            lines += [f'AIHOT 摘要摘录：{plain(item["summary"])}']
        lines += [f'[原始来源：{plain(item["source"], 70)}]({item["url"]}) · [AIHOT 整理与归属]({item["canonical"]})']
    if not ai:
        lines += ['今日 AIHOT 内容暂缺，不用旧内容补位。']
    lines += ['[数据来源：AIHOT](https://aihot.news/)',
        '仅供个人私密阅读；不要未经许可公开转发或商业再分发。']
    return '\n\n'.join(lines)


def send(body, now, key):
    # Explicitly support Turbo SCT keys only. Never accept arbitrary URLs.
    if not re.fullmatch(r'SCT[A-Za-z0-9]+', key or ''):
        raise SafeError('请配置 Server酱 Turbo 的 SCT 格式 SendKey；不支持 sctp/旧 SCK 格式。')
    data = urllib.parse.urlencode({'title': f'AIHOT 日报 {now.astimezone(CHINA):%m-%d}',
                                  'desp': body}).encode('utf-8')
    request = urllib.request.Request('https://sctapi.ftqq.com/' + key + '.send', data=data,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        # No POST retry: a timeout could mean the provider already accepted it.
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            result = json.loads(read_response(response))
    except Exception:
        raise SafeError('推送结果未知或请求失败；为避免重复推送未重试。先检查微信和 Server酱记录。') from None
    if result.get('code') != 0:
        raise SafeError('Server酱未返回成功；请查看服务端记录、额度和账户绑定。')
    print('Server酱已接受推送请求；这不等于微信已送达。')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--send', action='store_true', help='Actually send; default is a local preview.')
    parser.add_argument('--output', default='preview.md')
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    ai, notices = [], []
    try:
        ai = parse_ai(json.loads(get(AIHOT)), now)
        if not ai:
            notices.append('今日日报没有可解析且带来源链接的条目。')
    except SafeError as error:
        notices.append(str(error))
    except Exception:
        notices.append('AIHOT 暂时不可用或响应格式异常。')
    body = render(ai, notices, now)
    Path(args.output).write_text(body, encoding='utf-8')
    print(f'AIHOT 日报已生成：{len(ai)} 条；来源提示 {len(notices)} 项。')
    if args.send:
        send(body, now, os.environ.get('SERVERCHAN_SENDKEY', '').strip())
    if notices:
        print('内容不完整。请查看预览或收到的正文；本次标记失败以便 GitHub 提醒。')
        return 1
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except SafeError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except Exception:
        # Never expose a traceback/request object that might contain the SendKey.
        print('运行失败；详细异常已隐藏，防止泄露凭据。', file=sys.stderr)
        sys.exit(1)
