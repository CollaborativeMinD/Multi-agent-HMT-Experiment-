"""Materialize the reviewed, secret-free checkpoint before offline gates."""
import base64,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED="dfc0c085aba6bd80d600a5e4a120f011137155c3e17a49281986618434a23b6a"

def main():
    raw=gzip.decompress(base64.b64decode((ROOT/'checkpoint8192.b64').read_text(),validate=False))
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('CHECKPOINT_DIGEST_MISMATCH')
    files=json.loads(raw)
    if set(files)!={'frontier.jsonl','calls.jsonl','summary.json'}:raise ValueError('CHECKPOINT_FILES_INVALID')
    target=ROOT/'resume8192';target.mkdir(exist_ok=True)
    for name,content in files.items():(target/name).write_text(content)
    print('CHECKPOINT_VERIFIED='+EXPECTED)

if __name__=='__main__':main()
