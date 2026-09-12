import test from 'node:test';
import assert from 'node:assert/strict';
import {selectElections} from '../src/lib/elections.mjs';
test('elections exclude drafts, future stories, rumours and unrelated candidates',()=>{
 const base={slug:'valid',status:'published',publishedAt:'2026-09-09T10:00:00Z',confidence:'CONFIRMADO',tags:['eleições']};
 const rejected=[{status:'draft'},{publishedAt:'2026-09-11T10:00:00Z'},{confidence:'RELATO'},{tags:['Oscar','candidatos']},{confidence:'RUMOR'}].map(change=>({...base,...change}));
 assert.deepEqual(selectElections([base,...rejected],Date.parse('2026-09-10T10:00:00Z')).map(a=>a.slug),['valid']);
});
test('explicit election coverage flag prevents incidental candidate mentions from entering the panel',()=>{
 const base={slug:'direct',status:'published',publishedAt:'2026-09-09T10:00:00Z',confidence:'CONFIRMADO',tags:['Eleições 2026'],electionCoverage:true};
 const incidental={...base,slug:'incidental',electionCoverage:false};
 assert.deepEqual(selectElections([incidental,base],Date.parse('2026-09-10T10:00:00Z')).map(a=>a.slug),['direct']);
});
