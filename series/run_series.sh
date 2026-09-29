#!/usr/bin/env bash
set -euo pipefail
series_started=$SECONDS
for hand_slot in $(seq 1 200); do
  if (( SECONDS - series_started >= 19800 )); then
    PYTHONPATH=scripts:baseline:series python - <<'PY'
import campaign as c
state=c.read(c.OUT/'series.json');state.update(status='HOLD',reason='WORKFLOW_TIME_BOUND');c.finish(state,c.read(c.PLAN))
PY
    python series/report.py
    git add README.md evidence/whiz300
    git commit -m "Record 300-point series time-bound HOLD"
    git push origin HEAD:main
    exit 2
  fi
  set +e
  python series/campaign.py
  series_code=$?
  set -e
  python series/report.py
  git add README.md evidence/whiz300
  if ! git diff --cached --quiet; then
    git commit -m "Publish verified strict Whiz 300 hand ${hand_slot}"
    git push origin HEAD:main
  fi
  if [[ "$series_code" -ne 0 ]]; then exit "$series_code"; fi
  series_status=$(python -c 'import json; print(json.load(open("evidence/whiz300/series.json"))["status"])')
  if [[ "$series_status" == "COMPLETE" ]]; then exit 0; fi
done
exit 2
