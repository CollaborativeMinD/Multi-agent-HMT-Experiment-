"""Materialize the reviewed, secret-free checkpoint before offline gates."""
import base64,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED="86342d1d5d97fd2a0e4230404f2f0980c8ace8789f29b07e0a56553f31f402c3"

def main():
    raw=gzip.decompress(base64.b64decode((ROOT/'checkpoint240.b64').read_text(),validate=False))
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('CHECKPOINT_DIGEST_MISMATCH')
    files=json.loads(raw)
    if set(files)!={'frontier.jsonl','calls.jsonl','summary.json'}:raise ValueError('CHECKPOINT_FILES_INVALID')
    target=ROOT/'resume240';target.mkdir(exist_ok=True)
    for name,content in files.items():(target/name).write_text(content)
    print('CHECKPOINT_VERIFIED='+EXPECTED)

if __name__=='__main__':main()
