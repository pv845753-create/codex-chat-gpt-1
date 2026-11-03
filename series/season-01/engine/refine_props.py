import time
from produce import ROOT,render_episode
for name in ['02-perfectionism','06-quiet-work','08-burnout']:
 folder=ROOT/name
 while not (folder/'verification.json').exists():time.sleep(2)
 print('PROP REFINEMENT',name,flush=True)
 render_episode(folder)
print('PROP REFINEMENTS COMPLETE',flush=True)
