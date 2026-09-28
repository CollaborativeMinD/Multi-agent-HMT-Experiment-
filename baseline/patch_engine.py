from pathlib import Path
import hashlib,json
root=Path(__file__).parent/'node_modules/@game-hub/game-spades/dist/engine'
changes=[('core/constants.js',"{ '200': 200, '500': 500 }","{ '100': 100, '200': 200, '500': 500 }"),('internal/scoring.js','const bagsEarned = made ? totalTricks - contract : 0;','const bagsEarned = made ? totalTricks - contract : hands.filter(p => p.bid === NIL_BID).reduce((n, p) => n + p.tricksWon, 0);')]
receipt=[]
for name,old,new in changes:
 p=root/name;s=p.read_text();assert s.count(old)==1,(name,'source drift')
 after=s.replace(old,new);p.write_text(after)
 receipt.append({'file':name,'before':hashlib.sha256(s.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()})
print(json.dumps({'patches':receipt}))
