"""Exercise the installed distribution with an empty model cache."""

import subprocess
import sys
from pathlib import Path

import namedivider
from namedivider import BasicNameDivider, GBDTNameDivider, util
from namedivider.divider.config import GBDTNameDividerConfig

if not Path(namedivider.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
    raise SystemExit("Expected to import namedivider from the isolated environment")

# Keep downloaded models in the temporary smoke-test directory.
util.DEFAULT_CACHE_DIR = Path.cwd() / "model-cache"
gbdt_config = GBDTNameDividerConfig(
    path_family_names=util.get_family_name_pkl_default_path(),
    path_model=util.get_gbdt_model_v1_default_path(),
)
for divider in (BasicNameDivider(), GBDTNameDivider(config=gbdt_config)):
    result = str(divider.divide_name("田中太郎"))
    if result != "田中 太郎":
        raise SystemExit(f"{type(divider).__name__}: unexpected result {result!r}")

cli = Path(sys.executable).with_name("nmdiv")
subprocess.run([str(cli), "--help"], check=True)
result = subprocess.run([str(cli), "name", "田中太郎"], check=True, capture_output=True, text=True)
if result.stdout.strip() != "田中 太郎":
    raise SystemExit(f"CLI: unexpected result {result.stdout!r}")
print("Installed wheel smoke tests passed")
