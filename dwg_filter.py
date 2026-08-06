import hashlib
import json
import os
from collections import Counter
from pathlib import Path


FILTER_VERSION = 1
MANIFEST_NAME = "d2g-manifest.json"
GENERATED_DIRS = {"filtered_dwgs", "dwg_images"}


class FilterError(RuntimeError):
    pass


def _source_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_manifest(path):
    if not path.exists():
        return {"version": FILTER_VERSION, "files": {}}
    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if not isinstance(data.get("files"), dict):
            raise ValueError("missing files object")
        return data
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise FilterError("Could not read {}: {}".format(path, exc)) from exc


def _write_manifest(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with open(temporary, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)
    os.replace(temporary, path)


def _is_generated_path(path, root):
    relative_parts = path.relative_to(root).parts[:-1]
    return any(part.lower() in GENERATED_DIRS for part in relative_parts)


def _keep_layer(name):
    normalized = name.strip().upper()
    return normalized == "0" or "ETCH" in normalized


class DwgProjectFilter:
    def __init__(self, oda_path=None):
        self.oda_path = self._find_oda(oda_path)

    @staticmethod
    def _find_oda(configured_path):
        candidates = [
            configured_path,
            os.getenv("ODA_FILE_CONVERTER"),
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return str(Path(candidate))
        return None

    def scan(self, project_root):
        root = Path(project_root).resolve()
        if not root.is_dir():
            raise FilterError("Project folder does not exist: {}".format(root))

        records = []
        manifest_cache = {}
        source_files = sorted(
            path for path in root.rglob("*")
            if path.is_file()
            and path.suffix.lower() == ".dwg"
            and not _is_generated_path(path, root)
        )

        for source in source_files:
            material_dir = source.parent
            filtered_dir = material_dir / "Filtered_DWGs"
            images_dir = material_dir / "DWG_Images"
            manifest_path = filtered_dir / MANIFEST_NAME

            if manifest_path not in manifest_cache:
                manifest_cache[manifest_path] = _read_manifest(manifest_path)
            manifest = manifest_cache[manifest_path]
            entry = manifest["files"].get(source.name, {})
            fingerprint = _source_hash(source)
            fingerprint_matches = (
                entry.get("source_sha256") == fingerprint
                and entry.get("filter_version") == FILTER_VERSION
            )

            if fingerprint_matches:
                filtered_name = Path(entry.get("filtered_dwg", source.name)).name
                image_name = Path(entry.get("preview", source.stem + ".png")).name
                geo_name = Path(entry.get("geo", Path(filtered_name).stem + ".GEO")).name
            else:
                filtered_name = source.name
                image_name = source.stem + ".png"
                geo_name = source.stem + ".GEO"

            filtered_path = filtered_dir / filtered_name
            image_path = images_dir / image_name
            geo_path = filtered_dir / geo_name

            output_exists = filtered_path.exists()
            image_exists = image_path.exists()

            if output_exists and image_exists and fingerprint_matches:
                status = "complete" if geo_path.exists() else "ready"
            elif output_exists or image_exists:
                status = "conflict"
            else:
                status = "new"

            records.append({
                "source": str(source),
                "dwg": str(filtered_path),
                "image": str(image_path),
                "geo": str(geo_path),
                "material_dir": str(material_dir),
                "manifest": str(manifest_path),
                "source_sha256": fingerprint,
                "status": status,
            })
        return records

    @staticmethod
    def version_conflicts(records):
        for record in records:
            if record["status"] != "conflict":
                continue

            source = Path(record["source"])
            filtered_dir = Path(record["dwg"]).parent
            images_dir = Path(record["image"]).parent
            version = 2
            while True:
                stem = "{}_v{}".format(source.stem, version)
                filtered_path = filtered_dir / (stem + source.suffix)
                image_path = images_dir / (stem + ".png")
                geo_path = filtered_dir / (stem + ".GEO")
                if not filtered_path.exists() and not image_path.exists() and not geo_path.exists():
                    break
                version += 1

            record["dwg"] = str(filtered_path)
            record["image"] = str(image_path)
            record["geo"] = str(geo_path)
            record["status"] = "new"
        return records

    @staticmethod
    def summarize(records):
        statuses = Counter(record["status"] for record in records)
        material_folders = len({record["material_dir"] for record in records})
        return {
            "material_folders": material_folders,
            "total": len(records),
            "new": statuses["new"],
            "ready": statuses["ready"],
            "complete": statuses["complete"],
            "conflict": statuses["conflict"],
        }

    def process_new(self, records, progress=None):
        if any(record["status"] == "new" for record in records) and not self.oda_path:
            raise FilterError(
                "ODA File Converter is required. Install it from opendesign.com "
                "or set oda_converter_path in config.json."
            )

        new_records = [record for record in records if record["status"] == "new"]
        for index, record in enumerate(new_records, 1):
            if progress:
                progress(index, len(new_records), record)
            self._filter_one(record)

    def _filter_one(self, record):
        try:
            import ezdxf
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from ezdxf.addons import odafc
            from ezdxf.addons.drawing import Frontend, RenderContext
            from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        except ImportError as exc:
            raise FilterError(
                "DWG filtering dependencies are missing. Install ezdxf and matplotlib."
            ) from exc

        source = Path(record["source"])
        filtered_path = Path(record["dwg"])
        image_path = Path(record["image"])
        manifest_path = Path(record["manifest"])

        # Never replace an output, even if it appears after the preflight scan.
        if filtered_path.exists() or image_path.exists():
            raise FilterError("Output already exists for {}; skipped.".format(source.name))

        filtered_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        ezdxf.options.set("odafc-addon", "win_exec_path", self.oda_path)
        doc = odafc.readfile(source, audit=True)

        for layer in doc.layers:
            layer.on()
            layer.thaw()

        figure = plt.figure(figsize=(12, 8), dpi=150)
        axes = figure.add_axes([0, 0, 1, 1])
        axes.set_facecolor("#222831")
        Frontend(RenderContext(doc), MatplotlibBackend(axes)).draw_layout(
            doc.modelspace(), finalize=True
        )
        figure.savefig(
            image_path,
            dpi=150,
            facecolor="#222831",
            bbox_inches="tight",
            pad_inches=0.1,
        )
        plt.close(figure)

        try:
            for block in doc.blocks:
                for entity in list(block):
                    if (
                        entity.is_alive
                        and entity.dxf.hasattr("layer")
                        and not _keep_layer(entity.dxf.layer)
                    ):
                        block.delete_entity(entity)
            doc.audit()
            odafc.export_dwg(
                doc,
                filtered_path,
                version=doc.dxfversion,
                audit=True,
                replace=False,
            )
        except Exception:
            image_path.unlink(missing_ok=True)
            filtered_path.unlink(missing_ok=True)
            raise

        manifest = _read_manifest(manifest_path)
        manifest["version"] = FILTER_VERSION
        manifest["files"][source.name] = {
            "source": source.name,
            "source_sha256": record["source_sha256"],
            "filter_version": FILTER_VERSION,
            "filtered_dwg": filtered_path.name,
            "preview": image_path.name,
            "geo": Path(record["geo"]).name,
            "geo_complete": False,
        }
        _write_manifest(manifest_path, manifest)

    @staticmethod
    def mark_geo_complete(record):
        manifest_path = Path(record["manifest"])
        manifest = _read_manifest(manifest_path)
        source_name = Path(record["source"]).name
        entry = manifest["files"].get(source_name)
        if not entry:
            raise FilterError("No manifest entry for {}".format(source_name))
        entry["geo_complete"] = True
        _write_manifest(manifest_path, manifest)
