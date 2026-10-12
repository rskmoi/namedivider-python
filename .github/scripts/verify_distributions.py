"""Check release metadata and required assets without importing the package."""

import os
import runpy
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

version = runpy.run_path("namedivider/version.py")["__version__"]
expected = os.environ.get("EXPECTED_VERSION") or version
if expected != version:
    raise SystemExit(f"Expected version {expected!r}, but source version is {version!r}")

dist = Path("dist")
wheels = list(dist.glob("*.whl"))
sdists = list(dist.glob("*.tar.gz"))
if len(wheels) != 1 or len(sdists) != 1 or len(list(dist.iterdir())) != 2:
    raise SystemExit("Expected exactly one wheel and one sdist")

assets = {
    "namedivider/assets/kanji.csv",
    "namedivider/beta_bert_divider/config.json",
    "namedivider/beta_bert_divider/vocab.json",
}


def check_metadata(data: bytes) -> None:
    metadata = BytesParser().parsebytes(data)
    if metadata["Name"] != "namedivider-python" or metadata["Version"] != expected:
        raise SystemExit("Distribution name or version does not match the release")


with zipfile.ZipFile(wheels[0]) as wheel:
    if not wheels[0].name.endswith(("-py3-none-any.whl", "-py2.py3-none-any.whl")):
        raise SystemExit("Expected a platform-independent Python wheel")
    if not assets.issubset(wheel.namelist()):
        raise SystemExit("Wheel is missing required package assets")
    metadata_files = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
    if len(metadata_files) != 1:
        raise SystemExit("Expected exactly one wheel METADATA file")
    check_metadata(wheel.read(metadata_files[0]))

with tarfile.open(sdists[0]) as sdist:
    root = sdists[0].name.removesuffix(".tar.gz")
    if not {f"{root}/{asset}" for asset in assets}.issubset(sdist.getnames()):
        raise SystemExit("Sdist is missing required package assets")
    metadata_file = sdist.extractfile(f"{root}/PKG-INFO")
    if metadata_file is None:
        raise SystemExit("Sdist is missing PKG-INFO")
    check_metadata(metadata_file.read())

print(f"Verified wheel and sdist for namedivider-python {version}")
