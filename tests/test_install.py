import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('skill_install', ROOT / 'scripts/install-local.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        for name in module.RUNTIME:
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, p)
        self.target = self.base / 'with spaces 与中文' / module.NAME

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_runtime_installed_without_other_files(self):
        (self.source / 'private-note.txt').write_text('not part of runtime')
        module.install(self.source, self.target)
        got = sorted(p.relative_to(self.target).as_posix() for p in self.target.rglob('*') if p.is_file())
        self.assertEqual(got, sorted(module.RUNTIME))
        for name in module.RUNTIME:
            self.assertEqual((self.target / name).read_bytes(), (self.source / name).read_bytes())

    def test_repeat_refused_and_existing_content_preserved(self):
        module.install(self.source, self.target)
        (self.target / 'user-note').write_text('preserve')
        with self.assertRaises(FileExistsError):
            module.install(self.source, self.target)
        self.assertEqual((self.target / 'user-note').read_text(), 'preserve')

    def test_existing_regular_file_preserved(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text('user-file')
        with self.assertRaises(FileExistsError):
            module.install(self.source, self.target)
        self.assertEqual(self.target.read_text(), 'user-file')

    def test_broken_destination_symlink_preserved(self):
        self.target.parent.mkdir(parents=True)
        self.target.symlink_to(self.base / 'missing')
        with self.assertRaises(FileExistsError):
            module.install(self.source, self.target)
        self.assertTrue(self.target.is_symlink())

    def test_missing_runtime_refused_before_destination_created(self):
        (self.source / 'LICENSE').unlink()
        with self.assertRaises(ValueError):
            module.install(self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_runtime_symlink_refused(self):
        p = self.source / 'LICENSE'
        p.unlink()
        p.symlink_to(ROOT / 'LICENSE')
        with self.assertRaises(ValueError):
            module.install(self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_wrong_destination_name_refused(self):
        with self.assertRaises(ValueError):
            module.install(self.source, self.base / 'other-name')

    def test_default_install_rejects_legacy_duplicate(self):
        legacy = self.base / '.codex' / 'skills' / module.NAME
        legacy.parent.mkdir(parents=True)
        legacy.symlink_to(self.base / 'missing')
        env = {**os.environ, 'HOME': str(self.base)}
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install-local.py')],
                                env=env, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('legacy_install_exists', result.stderr)
        self.assertTrue(legacy.is_symlink())


if __name__ == '__main__':
    unittest.main()
