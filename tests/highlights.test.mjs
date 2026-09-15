import test from 'node:test';
import assert from 'node:assert/strict';
import {highlightFor,selectHighlights} from '../src/lib/highlights.mjs';
const now=Date.parse('2026-09-09T12:00:00Z');
const story={slug:'a',status:'published',publishedAt:'2026-09-09T10:00:00Z',confidence:'CONFIRMADO',relevance:90,sources:[{url:'https://a.example/news',organization:'A'},{url:'https://b.example/news',organization:'B'}]};
const review={level:'urgent',reviewedAt:'2026-09-09T11:00:00Z',expiresAt:'2026-09-09T13:00:00Z',reason:'Decisão confirmada com impacto imediato documentado.',evidenceURLs:story.sources.map(s=>s.url)};
test('important and normal reviews are not urgent',()=>{for(const level of ['normal','important'])assert.equal(highlightFor({...story,highlight:{...review,level}},now),null)});
test('only recent published facts can receive the strict urgent label',()=>{for(const change of [{status:'draft'},{confidence:'RUMOR'},{publishedAt:'invalid'},{publishedAt:'2026-09-10T10:00:00Z'},{publishedAt:'2026-09-08T12:00:00Z'}])assert.equal(highlightFor({...story,...change},now),null)});
test('ordinary recent stories do not receive a false urgent label',()=>assert.equal(highlightFor(story,now),null));
test('a documented review enters the panel with one neutral label',()=>assert.equal(highlightFor({...story,highlight:review},now).highlightLabel,'URGENTE'));
test('review requires evidence, independence and a valid expiry',()=>{assert.equal(highlightFor({...story,highlight:review},now).highlightLevel,'urgent');for(const change of [{expiresAt:'2026-09-09T11:30:00Z'},{expiresAt:'2026-09-10T00:00:00Z'},{reviewedAt:'2026-09-09T13:00:00Z'},{evidenceURLs:['https://fake.example']},{reason:''}])assert.equal(highlightFor({...story,highlight:{...review,...change}},now),null)});
test('unconfirmed reports cannot be elevated',()=>{assert.equal(highlightFor({...story,confidence:'RELATO',highlight:review},now),null)});
test('urgent panel never falls back to ordinary or old news',()=>{
 assert.deepEqual(selectHighlights([story,{...story,slug:'old',publishedAt:'2026-09-01T00:00:00Z'}],now),[]);
 const urgent={...story,slug:'urgent',highlight:review};
 assert.deepEqual(selectHighlights([story,urgent],now).map(x=>x.slug),['urgent']);
});
