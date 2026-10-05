"""Standalone fixture contract, preserving strict/recovered distinction."""
from pathlib import Path
import json, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
LANGUAGE = "json"
BIN = str(Path(sys.argv[1]).resolve())
cases = json.loads((ROOT / "fixtures/cases.json").read_text())
for filename, expected in cases["good"].items():
    path = ROOT / "fixtures" / filename
    data = path.read_bytes()
    result = subprocess.run([BIN, "symbols", str(path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, (path, result.stderr)
    doc = json.loads(result.stdout)
    assert doc["complete"] is True and doc["lang"] == LANGUAGE
    assert set(expected) <= {row["name"] for row in doc["symbols"]}
    for row in doc["symbols"]:
        lo, hi = row["start_byte"], row["end_byte"]
        assert 0 <= lo < hi <= len(data)
        assert data[lo:hi].decode("utf-8").strip()
        assert row["start"] == data[:lo].count(b"\n") + 1
    for command in ["tokens", "parse", "outline", "tags"]:
        result = subprocess.run([BIN, command, str(path)], capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, (path, command, result.stderr)
    result = subprocess.run([BIN, "check", str(path)], capture_output=True, text=True, timeout=30)
    assert (result.returncode == 0) == (LANGUAGE == "json")
for filename in cases["bad"]:
    result = subprocess.run([BIN, "symbols", str(ROOT / "fixtures" / filename)], capture_output=True, text=True, timeout=30)
    assert result.returncode != 0 and not result.stdout, (filename, result.stdout)
print(f"{LANGUAGE}: {len(cases['good'])} valid and {len(cases['bad'])} malformed fixtures passed")
