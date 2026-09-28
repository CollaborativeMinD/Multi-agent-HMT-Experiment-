import assert from 'node:assert/strict';
import {setup,whizLegal,whizApply} from './engine.mjs';
import {viewFor,isSpade} from '@game-hub/game-spades/engine';
import {decide} from '@game-hub/game-spades/bot';
import {scoreHand,winningTeam} from './node_modules/@game-hub/game-spades/dist/engine/internal/scoring.js';
const fixture=[{bid:0,tricksWon:2},{bid:4,tricksWon:4},{bid:5,tricksWon:3},{bid:4,tricksWon:4}].map(x=>({...x,blindNil:false}));
const scored=scoreHand(fixture,[0,0],[0,0]);assert.equal(scored.teams[0].score,-148);assert.equal(scored.teams[0].bagsEarned,2);
assert.equal(scoreHand(fixture,[0,0],[9,0]).teams[0].bags,1);
assert.equal(winningTeam([100,100],100),null);assert.equal(winningTeam([100,99],100),0);
let matches=[];
for(const seed of [1,7,19]){
 let s=setup(seed,'test'),initial=s,actions=[];assert.equal(s.targetScore,100);
 while(s.status!=='ended'&&actions.length<3000){
  const p=s.players[s.activePlayerIndex],v=viewFor(s,p.id),legal=whizLegal(s);
  assert(!('deckSeed' in v));assert(v.players.every(x=>x.id===p.id?Array.isArray(x.hand):x.hand===null));
  let a=decide(v,p.id);if(a.type==='BID')a={type:'BID',bid:a.bid===0?0:p.hand.filter(isSpade).length};
  if(s.phase==='bidding'){
   assert(legal.every(x=>x.bid===0||x.bid===p.hand.filter(isSpade).length));
   let bad=1;while(legal.some(x=>x.bid===bad))bad++;
   assert.throws(()=>whizApply(s,p.id,{type:'BID',bid:bad}));
  }
  actions.push({id:p.id,a});s=whizApply(s,p.id,a);
 }
 assert.equal(s.status,'ended');let replay=initial;for(const {id,a} of actions)replay=whizApply(replay,id,a);assert.deepEqual(replay,s);
 matches.push({seed,hands:s.handNumber,actions:actions.length,scores:s.scores});
}
console.log(JSON.stringify({status:'PASS',gates:['nil_bags_when_set','bag_rollover','100_target','tie_continue','whiz_reject','private_views','full_replay'],matches}));
