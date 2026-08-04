"""Tests for python-async-architect/scripts/detect_async_blocking.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests._loader import load

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestDetectAsyncBlocking(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("detect_async_blocking")

    def test_flags_blocking_calls_in_async(self) -> None:
        hits = self.mod.detect(FIXTURES / "async_blocking" / "app.py")
        names = [name for _lineno, name in hits]
        self.assertIn("time.sleep", names)
        self.assertIn("requests.get", names)

    def test_does_not_flag_sync_helper(self) -> None:
        hits = self.mod.detect(FIXTURES / "async_blocking" / "app.py")
        # Only calls inside async functions are flagged; the sync helper uses
        # time.sleep but must not be reported.
        self.assertEqual(len(hits), 2)

    def test_safe_async_untouched(self) -> None:
        hits = self.mod.detect(FIXTURES / "async_blocking" / "app.py")
        names = [name for _lineno, name in hits]
        self.assertNotIn("client.get", names)

    def test_flags_blocking_call_in_nested_function(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import time\n\nasync def outer():\n"
                "    def inner():\n"
                "        time.sleep(1)\n"
                "    inner()\n",
                encoding="utf-8",
            )
            hits = self.mod.detect(file)
            self.assertIn("time.sleep", [name for _lineno, name in hits])

    def test_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "ok.py"
            file.write_text(
                "import asyncio\n\nasync def run(client, uid):\n"
                "    r = await client.get(f'/u/{uid}', timeout=5.0)\n"
                "    return r.json()\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_run_in_executor_lambda_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, time\n\nasync def run():\n"
                "    await asyncio.run_in_executor(None, lambda: time.sleep(1))\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_to_thread_nested_helper_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, time\n\nasync def run():\n"
                "    def helper():\n"
                "        time.sleep(1)\n"
                "    await asyncio.to_thread(helper)\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_to_thread_lambda_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, time\n\nasync def run():\n"
                "    await asyncio.to_thread(lambda: requests.get('/x'))\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_executor_lambda_via_variable_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, requests\n\nasync def run():\n"
                "    fetch = lambda: requests.get('http://x')\n"
                "    await asyncio.run_in_executor(None, fetch)\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_loop_run_in_executor_lambda_via_variable_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, requests\n\nasync def run():\n"
                "    loop = asyncio.get_running_loop()\n"
                "    fn = lambda: requests.get('http://x')\n"
                "    await loop.run_in_executor(None, fn)\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_to_thread_lambda_via_variable_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, requests\n\nasync def run():\n"
                "    fn = lambda: requests.get('http://x')\n"
                "    await asyncio.to_thread(fn)\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_executor_def_via_alias_variable_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, requests\n\nasync def run():\n"
                "    def sync_http():\n"
                "        return requests.get('http://x')\n"
                "    fetch = sync_http\n"
                "    await asyncio.to_thread(fetch)\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_executor_lambda_assigned_after_call_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, requests\n\nasync def run():\n"
                "    await asyncio.run_in_executor(None, fetch)\n"
                "    fetch = lambda: requests.get('http://x')\n",
                encoding="utf-8",
            )
            self.assertEqual(self.mod.detect(file), [])

    def test_direct_nested_blocking_call_still_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "app.py"
            file.write_text(
                "import asyncio, requests\n\nasync def run():\n"
                "    fetch = lambda: requests.get('http://x')\n"
                "    return fetch()\n",
                encoding="utf-8",
            )
            hits = self.mod.detect(file)
            self.assertIn("requests.get", [name for _lineno, name in hits])


if __name__ == "__main__":
    unittest.main()
