import {createGame,applyAction,legalActions,viewFor,isSpade} from '@game-hub/game-spades/engine';
import {mulberry32} from '@game-hub/kernel';
import {decide} from '@game-hub/game-spades/bot';
import readline from 'node:readline';
import {createHash} from 'node:crypto';
let state,initial,events=[];
export function whizLegal(s){
 const p=s.players[s.activePlayerIndex];
 return legalActions(s,p.id).filter(a=>a.type!=='BID'||a.bid===0||a.bid===p.hand.filter(isSpade).length);
}
export function whizApply(s,id,a){
 if(id!==s.players[s.activePlayerIndex].id||!whizLegal(s).some(x=>JSON.stringify(x)===JSON.stringify(a)))throw Error('ILLEGAL_ACTION');
 return applyAction(s,id,a);
}
export function setup(seed,id,target=100){
 if(![100,300].includes(target))throw Error('TARGET_NOT_ADMITTED');
 return createGame({id,players:['North','East','South','West'].map(name=>({name})),rng:mulberry32(seed),options:{target:String(target),blindNil:false}});
}
function hash(s){return createHash('sha256').update(JSON.stringify(s)).digest('hex');}
function snapshot(s){const {deckSeed,log,...rest}=s;return rest;}
function observe(s){
 const p=s.players[s.activePlayerIndex],v=viewFor(s,p.id);
 if('deckSeed' in v||v.players.some(x=>x.id!==p.id&&x.hand!==null))throw Error('PRIVATE_VIEW_BREACH');
 const lastDeal=v.log.map(x=>x.type).lastIndexOf('DEAL');
 const history=v.log.slice(Math.max(0,lastDeal)).filter(x=>['PLAY','TRICK','BID'].includes(x.type));
 const {log,...visible}=v;
 return {...visible,history,you:p.id,partner:s.players[(s.activePlayerIndex+2)%4].id,legal:whizLegal(s)};
}
function dispatch(cmd){
 if(cmd.op==='init'){state=setup(cmd.seed,cmd.id,cmd.target??100);initial=state;events=[];}
 if(cmd.op==='step'){
  const before=state,player=state.players[state.activePlayerIndex].id;
  state=whizApply(state,player,cmd.action);events.push({player,action:cmd.action});
  return {snapshot:snapshot(state),hash:hash(state),newLog:state.log.slice(before.log.length)};
 }
 if(cmd.op==='observe')return observe(state);
 if(cmd.op==='bot')return decide(viewFor(state,state.players[state.activePlayerIndex].id),state.players[state.activePlayerIndex].id);
 if(cmd.op==='verify'){
  let replay=initial;for(const e of events)replay=whizApply(replay,e.player,e.action);
  if(hash(replay)!==hash(state))throw Error('REPLAY_MISMATCH');
  return {replay_verified:true,final_hash:hash(state),actions:events.length,status:state.status,log:state.log};
 }
 return {snapshot:snapshot(state),hash:hash(state)};
}
if(process.argv[1]?.split('/').pop()==='engine.mjs'){
 const rl=readline.createInterface({input:process.stdin});
 for await(const line of rl){try{console.log(JSON.stringify({ok:true,result:dispatch(JSON.parse(line))}));}catch{console.log(JSON.stringify({ok:false,reason:'ENGINE_REJECTED'}));}}
}
