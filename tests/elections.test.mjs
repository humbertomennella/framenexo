import test from 'node:test';
import assert from 'node:assert/strict';
import {selectElections} from '../src/lib/elections.mjs';
test('elections exclude drafts, future stories, rumours and unrelated candidates',()=>{
 const base={slug:'valid',status:'published',publishedAt:'2026-09-09T10:00:00Z',confidence:'CONFIRMADO',tags:['eleições']};
 const rejected=[{status:'draft'},{publishedAt:'2026-09-11T10:00:00Z'},{confidence:'RELATO'},{tags:['Oscar','candidatos']},{confidence:'RUMOR'}].map(change=>({...base,...change}));
 assert.deepEqual(selectElections([base,...rejected],Date.parse('2026-09-10T10:00:00Z')).map(a=>a.slug),['valid']);
});
