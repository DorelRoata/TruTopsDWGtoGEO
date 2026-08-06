import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from dwg_filter import DwgProjectFilter, FILTER_VERSION, MANIFEST_NAME


class ProjectScanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.material = self.root / "11GA2B"
        self.material.mkdir()
        self.source = self.material / "PART-001.DWG"
        self.source.write_bytes(b"sample dwg")
        self.project_filter = DwgProjectFilter()

    def tearDown(self):
        self.temporary.cleanup()

    def _write_ready_outputs(self, geo_complete=False):
        filtered_dir = self.material / "Filtered_DWGs"
        images_dir = self.material / "DWG_Images"
        filtered_dir.mkdir()
        images_dir.mkdir()
        (filtered_dir / self.source.name).write_bytes(b"filtered")
        (images_dir / "PART-001.png").write_bytes(b"preview")
        digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        manifest = {
            "version": FILTER_VERSION,
            "files": {
                self.source.name: {
                    "source_sha256": digest,
                    "filter_version": FILTER_VERSION,
                    "geo_complete": geo_complete,
                }
            },
        }
        (filtered_dir / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")

    def test_new_source_is_discovered(self):
        records = self.project_filter.scan(self.root)
        self.assertEqual([record["status"] for record in records], ["new"])

    def test_existing_output_without_manifest_is_conflict(self):
        filtered_dir = self.material / "Filtered_DWGs"
        filtered_dir.mkdir()
        (filtered_dir / self.source.name).write_bytes(b"do not replace")
        records = self.project_filter.scan(self.root)
        self.assertEqual(records[0]["status"], "conflict")

    def test_matching_manifest_is_ready(self):
        self._write_ready_outputs()
        records = self.project_filter.scan(self.root)
        self.assertEqual(records[0]["status"], "ready")

    def test_existing_geo_is_complete(self):
        self._write_ready_outputs()
        (self.material / "Filtered_DWGs" / "PART-001.GEO").write_bytes(b"geo")
        records = self.project_filter.scan(self.root)
        self.assertEqual(records[0]["status"], "complete")

    def test_manifest_does_not_hide_missing_geo(self):
        self._write_ready_outputs(geo_complete=True)
        records = self.project_filter.scan(self.root)
        self.assertEqual(records[0]["status"], "ready")

    def test_changed_source_is_conflict(self):
        self._write_ready_outputs()
        self.source.write_bytes(b"changed source")
        records = self.project_filter.scan(self.root)
        self.assertEqual(records[0]["status"], "conflict")

    def test_conflict_can_use_next_version_without_overwrite(self):
        self._write_ready_outputs()
        records = self.project_filter.scan(self.root)
        self.source.write_bytes(b"changed source")
        records = self.project_filter.scan(self.root)
        self.project_filter.version_conflicts(records)
        self.assertEqual(records[0]["status"], "new")
        self.assertEqual(Path(records[0]["dwg"]).name, "PART-001_v2.DWG")
        self.assertTrue((self.material / "Filtered_DWGs" / "PART-001.DWG").exists())

    def test_scan_uses_version_recorded_in_manifest(self):
        self._write_ready_outputs()
        filtered_dir = self.material / "Filtered_DWGs"
        images_dir = self.material / "DWG_Images"
        (filtered_dir / "PART-001.DWG").rename(filtered_dir / "PART-001_v2.DWG")
        (images_dir / "PART-001.png").rename(images_dir / "PART-001_v2.png")
        manifest_path = filtered_dir / MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = manifest["files"][self.source.name]
        entry["filtered_dwg"] = "PART-001_v2.DWG"
        entry["preview"] = "PART-001_v2.png"
        entry["geo"] = "PART-001_v2.GEO"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        records = self.project_filter.scan(self.root)
        self.assertEqual(records[0]["status"], "ready")
        self.assertEqual(Path(records[0]["dwg"]).name, "PART-001_v2.DWG")

    def test_generated_dwgs_are_not_sources(self):
        self._write_ready_outputs()
        records = self.project_filter.scan(self.root)
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
