"""Bounded RFC JSON syntax oracle; deterministic source-only test data."""
from pathlib import Path
import json
import random
import subprocess
import sys
import tempfile

BIN = str(Path(sys.argv[1]).resolve())
GOOD = [None, True, False, 0, -1, 1.25, '日本語 🌳', [], {}, {'name':'demo','items':[1,{'enabled':True},None]}]
BAD = ['', '01','-','1.','+1','.1','1e','1e+','NaN','Infinity','[1,]','{"x":1,}','{"x":}','[1 2]','{}{}','true false','{x:1}',"'x'",'"\\q"','"\\uZZZZ"','"line\nbreak"','/*x*/null','[','}','{"x":[1,2}','\ufeff{}']
rng = random.Random(20261005)
def value(depth):
    choices = [None, True, False, rng.randint(-10000,10000), rng.uniform(-10,10), '日本語 🌳 \\\n"']
    if depth < 4:
        choices.extend([[value(depth+1) for _ in range(rng.randrange(5))], {f'key{rng.randrange(100)}':value(depth+1) for _ in range(rng.randrange(5))}])
    return rng.choice(choices)
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / 'oracle.json'
    def check(text, expected):
        path.write_text(text)
        result = subprocess.run([BIN, 'check', str(path)], capture_output=True, text=True, timeout=30)
        assert (result.returncode == 0) == expected, (text, result.stdout, result.stderr)
    for obj in GOOD:
        for ascii_only in (False, True): check(json.dumps(obj, ensure_ascii=ascii_only, allow_nan=False), True)
    for text in BAD:
        try: json.loads(text, parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        except ValueError: pass
        else: raise AssertionError(('oracle accepted invalid fixture', text))
        check(text, False)
    for case in range(200): check(json.dumps(value(0), ensure_ascii=case%2==0, allow_nan=False, indent=2 if case%3==0 else None), True)
print('JSON oracle passed: 20 fixed serializations, 26 malformed cases, 200 seeded documents')
