from pathlib import Path
import json,time
from produce import render_episode,ROOT
pending=[p.parent for p in sorted(ROOT.glob('*/episode.json')) if int(json.loads(p.read_text())['id'])>=3]
started=time.monotonic()
while pending:
 ready=[]
 for p in pending:
  try:
   m=json.loads((p/'metrics.json').read_text())
   if m['duration_seconds']>=300:ready.append(p)
  except (FileNotFoundError,json.JSONDecodeError):pass
 if ready:
  p=ready[0];render_episode(p);pending.remove(p)
 elif time.monotonic()-started>3600:raise SystemExit('Audio prerequisites unavailable: '+str(pending))
 else:time.sleep(2)
print('ALL EIGHT QUEUED VIDEOS COMPLETE',flush=True)
