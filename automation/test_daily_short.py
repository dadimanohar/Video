import unittest
from datetime import datetime, timezone
from daily_short import ArticleTextParser, is_official_url, is_recent_published, parse_published_date, wait_for_video_processing


class SourceValidationTests(unittest.TestCase):
    def test_official_domains_and_https(self):
        self.assertTrue(is_official_url("https://openai.com/news/example"))
        self.assertTrue(is_official_url("https://blog.google/technology/ai/example"))
        self.assertTrue(is_official_url("https://blogs.nvidia.com/example"))
        self.assertFalse(is_official_url("http://openai.com/news/example"))
        self.assertFalse(is_official_url("https://openai.com.attacker.invalid/news"))
        self.assertFalse(is_official_url("https://example.com/?next=https://openai.com"))

    def test_article_parser_skips_navigation_and_reads_og_description(self):
        parser = ArticleTextParser()
        parser.feed('<meta property="og:description" content="Useful summary"><nav>Menu</nav><article><p>Article text</p></article><script>bad()</script>')
        extracted = " ".join(parser.parts)
        self.assertIn("Useful summary", extracted)
        self.assertIn("Article text", extracted)
        self.assertNotIn("Menu", extracted)
        self.assertNotIn("bad()", extracted)

    def test_rfc_and_iso_dates(self):
        self.assertIsNotNone(parse_published_date("Sat, 31 Oct 2026 00:00:00 GMT"))
        self.assertIsNotNone(parse_published_date("2026-10-31T00:00:00Z"))
        self.assertIsNone(parse_published_date("not a date"))

    def test_freshness_window_and_future_guard(self):
        now = datetime(2026, 10, 31, tzinfo=timezone.utc)
        self.assertTrue(is_recent_published("2026-10-30T00:00:00Z", now))
        self.assertFalse(is_recent_published("", now))
        self.assertFalse(is_recent_published("2026-10-15T00:00:00Z", now))
        self.assertFalse(is_recent_published("2026-11-02T00:00:00Z", now))

    def test_gemini_request_uses_structured_json_without_legacy_sampling_fields(self):
        import json
        from unittest.mock import patch
        from daily_short import generate_script

        source = {
            "title": "A current AI update",
            "url": "https://openai.com/news/example",
            "summary": "Official summary",
            "published": "Sat, 31 Oct 2026 00:00:00 GMT",
            "domain": "openai.com",
            "article_context": "Detailed official article context."
        }
        script = (
            "This is a verified update from the official publisher. " * 12
        ).strip()
        model_response = {
            "status": "ready",
            "title": "A verified AI update",
            "script": script,
            "description": "A factual summary.",
            "used_urls": [source["url"]]
        }
        fake_response = type("FakeResponse", (), {
            "status_code": 200,
            "json": lambda self: {
                "candidates": [{
                    "content": {"parts": [{"text": json.dumps(model_response)}]}
                }]
            }
        })()
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("daily_short.requests.post", return_value=fake_response) as post:
                result = generate_script([source])
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["generationConfig"]["responseMimeType"], "application/json")
        self.assertNotIn("temperature", payload["generationConfig"])
        self.assertEqual(result["sources"], [source])

 
class FakeRequest:
    def __init__(self, payload):
        self.payload = payload
    def execute(self):
        return self.payload


class FakeVideos:
    def __init__(self, payload):
        self.payload = payload
    def list(self, **kwargs):
        return FakeRequest(self.payload)


class FakeYoutube:
    def __init__(self, payload):
        self.payload = payload
    def videos(self):
        return FakeVideos(self.payload)


class UploadVerificationTests(unittest.TestCase):
    def test_processing_and_privacy_are_verified(self):
        youtube = FakeYoutube({"items": [{
            "id": "abc123",
            "status": {"privacyStatus": "private"},
            "processingDetails": {"processingStatus": "succeeded"}
        }]})
        result = wait_for_video_processing(youtube, "abc123", "private")
        self.assertEqual(result["id"], "abc123")

    def test_processing_failure_is_not_reported_as_success(self):
        youtube = FakeYoutube({"items": [{
            "status": {"privacyStatus": "private"},
            "processingDetails": {"processingStatus": "failed"}
        }]})
        with self.assertRaisesRegex(RuntimeError, "processing failed"):
            wait_for_video_processing(youtube, "abc123", "private")


if __name__ == "__main__":
    unittest.main()
