import assert from 'node:assert/strict';
import {setup,whizApply,whizLegal} from '../baseline/engine.mjs';
import {scoreHand,winningTeam} from '../baseline/node_modules/@game-hub/game-spades/dist/engine/internal/scoring.js';
assert.equal(winningTeam([299,200],300),null);assert.equal(winningTeam([300,299],300),0);assert.equal(winningTeam([300,300],300),null);
for(const seed of [101,202,303,404,505]){
 let s=setup(seed,'tracer',300),initial=s;const actions=[];
 assert.equal(s.targetScore,300);
 while(s.status!=='ended'&&actions.length<1120){const p=s.players[s.activePlayerIndex].id,a=whizLegal(s).at(-1);actions.push([p,a]);s=whizApply(s,p,a);}
 assert.equal(s.status,'ended');assert(Math.max(...s.scores)>=300);
 let again=initial;for(const [p,a]of actions)again=whizApply(again,p,a);assert.deepEqual(again,s);
 console.log(JSON.stringify({kind:'SYNTHETIC_TRACER_NOT_MODEL_RESULT',seed,hands:s.handNumber,scores:s.scores,actions:actions.length}));
}
assert.throws(()=>setup(1,'bad',500));
