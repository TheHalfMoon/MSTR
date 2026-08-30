from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPOSITORY_ROOT / "colab" / "mstr_t029_quantize.py"


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("mstr_t029_quantize", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_replaces_non_utf8_subprocess_output() -> None:
    runner = _load_runner()
    code = "import os; os.write(2, b'quantizer\\xc4\\xffoutput')"

    return_code, output = runner.run([sys.executable, "-c", code])

    assert return_code == 0
    assert "quantizer" in output
    assert "output" in output
    assert "\ufffd" in output


def test_run_preserves_utf8_subprocess_output() -> None:
    runner = _load_runner()
    code = "import os; os.write(1, 'Q4_K_M ok\\n'.encode('utf-8'))"

    return_code, output = runner.run([sys.executable, "-c", code], env=os.environ.copy())

    assert return_code == 0
    assert output == "Q4_K_M ok\n"
