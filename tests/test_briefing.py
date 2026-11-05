import contextlib
import io
import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
import briefing as b

NOW = datetime(2026, 11, 5, 0, 15, tzinfo=timezone.utc)

def ai_payload(date='2026-11-05'):
    return {'schemaVersion': 1, 'report': {'date': date, 'sections': [{'label': '产品', 'items': [
        {'title': '模型发布', 'summary': '摘要', 'source': {'name': '官方'},
         'links': {'original': 'https://example.com/model', 'aihot': 'https://aihot.news/items/a'}},
        {'title': 'Figma 创意工具', 'summary': '摘要', 'source': {'name': '官方'},
         'links': {'original': 'https://example.com/design', 'aihot': 'https://aihot.news/items/b'}}]}]}}

class BriefingTests(unittest.TestCase):
    def test_local_preview_does_not_log_body(self):
        with tempfile.TemporaryDirectory() as directory:
            output = str(Path(directory) / 'preview.md')
            with patch('sys.argv', ['briefing.py', '--output', output]), patch.object(b, 'get', return_value=b'{}'), contextlib.redirect_stdout(io.StringIO()) as log:
                self.assertEqual(b.main(), 1)
            body = Path(output).read_text()
            self.assertIn('AIHOT 日报', body)
            self.assertNotIn('# AIHOT 日报', log.getvalue())
            self.assertNotIn('https://', log.getvalue())
    def test_workflow_has_no_public_content_export(self):
        workflow = (Path(__file__).parents[1] / '.github/workflows/daily.yml').read_text()
        self.assertNotIn('GITHUB_STEP_SUMMARY', workflow)
        self.assertNotIn('upload-artifact', workflow)
        self.assertNotIn('cat ', workflow)
        self.assertIn('rm -f "$RUNNER_TEMP/private-briefing.md"', workflow)
        self.assertIn('[ -z "$SERVERCHAN_SENDKEY" ]', workflow)
    def test_fresh_ai_preserves_source_order(self):
        self.assertEqual(b.parse_ai(ai_payload(), NOW)[0]['title'], '模型发布')
    def test_stale_ai(self):
        with self.assertRaises(b.SafeError): b.parse_ai(ai_payload('2026-11-04'), NOW)
    def test_china_date_boundary(self):
        self.assertEqual(len(b.parse_ai(ai_payload(), datetime(2026,11,4,16,1,tzinfo=timezone.utc))), 2)
    def test_schema_change(self):
        p = ai_payload(); p['schemaVersion'] = 2
        with self.assertRaises(b.SafeError): b.parse_ai(p, NOW)
    def test_duplicate_ai(self):
        p = ai_payload(); p['report']['sections'] *= 2
        self.assertEqual(len(b.parse_ai(p, NOW)), 2)
    def test_missing_source_is_skipped(self):
        p = ai_payload(); p['report']['sections'][0]['items'][0]['links'] = {}
        self.assertEqual(len(b.parse_ai(p, NOW)), 1)
    def test_unsafe_url(self):
        for url in ['javascript:alert(1)', 'http://example.com', 'https://user:pass@example.com', None]:
            self.assertEqual(b.safe_url(url), '')
    def test_markdown_escape(self): self.assertIn('\\[', b.plain('[evil](x)'))
    def test_honest_labels(self):
        text = b.render([], ['测试提示'], NOW)
        for word in ['没有另行调用大模型', '未独立核验', '测试提示']:
            self.assertIn(word, text)
    def test_reject_unsupported_key_without_request(self):
        with patch('urllib.request.build_opener') as opener:
            with self.assertRaises(b.SafeError): b.send('body', NOW, 'sctp_example')
            opener.assert_not_called()
    def test_no_secret_in_failure_and_no_post_retry(self):
        with patch('urllib.request.build_opener') as opener:
            opener.return_value.open.side_effect = RuntimeError('SCTtestSecret')
            with self.assertRaises(b.SafeError) as ctx: b.send('body', NOW, 'SCTtestSecret')
            self.assertNotIn('SCTtestSecret', str(ctx.exception))
            self.assertEqual(opener.return_value.open.call_count, 1)
    def test_redirect_blocked(self):
        with self.assertRaises(b.SafeError): b.NoRedirect().redirect_request(None,None,302,'',{},'https://evil.test')
    def test_success_is_provider_acceptance(self):
        with patch('urllib.request.build_opener') as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.headers = {}; response.read.return_value = b'{"code":0}'
            with contextlib.redirect_stdout(io.StringIO()) as out: b.send('body', NOW, 'SCTtestKey')
            self.assertIn('不等于微信已送达', out.getvalue())
    def test_provider_error(self):
        with patch('urllib.request.build_opener') as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.headers = {}; response.read.return_value = b'{"code":40001}'
            with self.assertRaises(b.SafeError): b.send('body', NOW, 'SCTtestKey')

if __name__ == '__main__': unittest.main()
