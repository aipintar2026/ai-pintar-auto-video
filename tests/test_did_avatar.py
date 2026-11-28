import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.did_avatar import create_avatar_video


class FakeResponse:
    def __init__(self, data=None, payload=b""):
        self.data = data
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def iter_content(self, chunk_size):
        yield self.payload


class DIDAvatarAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audio = Path(self.tmp.name) / "voice.mp3"
        self.output = Path(self.tmp.name) / "presenter.mp4"
        self.audio.write_bytes(b"audio")

    def tearDown(self):
        self.tmp.cleanup()

    def test_success_flow_mocked_no_provider_calls(self):
        post_responses = [
            FakeResponse({"url": "https://audio.example/upload.mp3"}),
            FakeResponse({"id": "mock-talk-id"}),
        ]
        get_responses = [
            FakeResponse({"status": "done", "result_url": "https://video.example/result.mp4"}),
            FakeResponse(payload=b"x" * 120_000),
        ]
        with patch("engine.did_avatar.requests.post", side_effect=post_responses), \
             patch("engine.did_avatar.requests.get", side_effect=get_responses), \
             patch("engine.did_avatar.time.sleep", return_value=None):
            result = create_avatar_video(
                self.audio, self.output,
                source_url="https://image.example/master.jpg",
                api_key="mock-key",
            )
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["talk_id"], "mock-talk-id")
        self.assertEqual(self.output.stat().st_size, 120_000)

    def test_missing_key_fails_closed(self):
        with patch.dict("os.environ", {"DID_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "DID_API_KEY"):
                create_avatar_video(self.audio, self.output, source_url="https://image.example/master.jpg")

    def test_non_https_master_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "HTTPS"):
            create_avatar_video(self.audio, self.output, source_url="http://image.example/master.jpg", api_key="mock-key")


if __name__ == "__main__":
    unittest.main()
