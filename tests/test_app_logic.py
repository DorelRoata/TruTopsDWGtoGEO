import unittest
from unittest import mock

import app


class DummyConfig:
    def __init__(self, policy):
        self.policy = policy

    def get(self, *keys):
        if keys == ("existing_geo_policy",):
            return self.policy
        return None


class D2GLogicTests(unittest.TestCase):
    def make_runner(self, policy):
        runner = app.AutomationRunner.__new__(app.AutomationRunner)
        runner.config = DummyConfig(policy)
        return runner

    def test_relative_position_follows_window(self):
        original = (100, 200, 1100, 700)
        relative = app.to_relative_position(600, 450, original)
        self.assertEqual([0.5, 0.5], relative)
        self.assertEqual(
            (1000, 700),
            app.from_relative_position(relative, (500, 450, 1500, 950)),
        )

    def test_file_dialog_pastes_only_filename(self):
        runner = self.make_runner("skip_existing")
        runner._copy_to_clipboard = mock.Mock()
        runner._hotkey = mock.Mock()
        runner._press = mock.Mock()

        runner._open_file_from_dialog(r"C:\jobs\part.dwg")

        runner._copy_to_clipboard.assert_called_once_with("part.dwg")
        self.assertEqual(
            [mock.call('ctrl', 'a', description="Select filename"),
             mock.call('ctrl', 'v', description="Paste DWG filename")],
            runner._hotkey.call_args_list,
        )
        runner._press.assert_called_once_with('enter', "Open drawing")

    @mock.patch("app.os.path.exists", return_value=True)
    def test_skip_existing_geo_policy(self, _exists):
        dwg = r"C:\jobs\part.dwg"
        self.assertEqual(
            "GEO already exists",
            self.make_runner("skip_existing")._skip_reason(dwg),
        )
        self.assertIsNone(self.make_runner("replace_existing")._skip_reason(dwg))

    @mock.patch("app.os.path.getmtime", return_value=10)
    @mock.patch("app.os.listdir", return_value=["part_1.geo", "part-other.geo"])
    @mock.patch("app.os.path.exists", return_value=False)
    def test_numbered_trutops_geo_is_detected(self, _exists, _listdir, _getmtime):
        reason = self.make_runner("skip_existing")._skip_reason(r"C:\jobs\part.dwg")
        self.assertEqual("GEO already exists", reason)

    @mock.patch("app.os.path.getmtime")
    @mock.patch("app.os.path.exists", return_value=True)
    def test_newer_only_processes_changed_dwg(self, _exists, getmtime):
        dwg = r"C:\jobs\part.dwg"
        geo = r"C:\jobs\part.geo"
        getmtime.side_effect = lambda path: 20 if path == dwg else 10
        self.assertIsNone(self.make_runner("newer_only")._skip_reason(dwg))
        getmtime.side_effect = lambda path: 10 if path == dwg else 20
        self.assertEqual(
            "GEO is newer than DWG",
            self.make_runner("newer_only")._skip_reason(dwg),
        )


if __name__ == "__main__":
    unittest.main()
