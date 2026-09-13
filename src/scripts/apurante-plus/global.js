import {read,write,toggle,toggleSaved,STORAGE_KEY} from './store.js';
function syncSaved(state=read()){
  const saved=new Set(state.saved);
  document.querySelectorAll('[data-ap-save]').forEach(button=>{const active=saved.has(button.dataset.slug||'');button.setAttribute('aria-pressed',String(active));button.classList.toggle('is-saved',active);const label=button.querySelector('[data-ap-save-label]');if(label)label.textContent=active?'Salvo':'Salvar';});
  document.querySelectorAll('[data-plus-actions]').forEach(root=>{const button=root.querySelector('[data-save-article]');if(!button)return;const active=saved.has(root.dataset.slug||'');button.setAttribute('aria-pressed',String(active));button.textContent=active?'Salva ✓':'Salvar matéria';});
}
function syncTopics(state=read()){
  document.querySelectorAll('[data-plus-actions]').forEach(root=>{const tags=JSON.parse(root.dataset.tags||'[]');root.querySelectorAll('[data-topic]').forEach(button=>{const active=state.topics.includes(button.dataset.topic||'');button.setAttribute('aria-pressed',String(active));button.classList.toggle('is-active',active);});const follow=root.querySelector('[data-follow-topic]');if(follow)follow.textContent=tags.some(tag=>state.topics.includes(tag))?'Assuntos seguidos ✓':'Seguir assunto';});
}
const ordered=(state,categories)=>[...state.home.order.filter(c=>categories.includes(c)),...categories.filter(c=>!state.home.order.includes(c))];
export function applyHome(state=read()){
  const host=document.querySelector('[data-ap-home-sections]');if(!host)return;
  const blocks=[...host.querySelectorAll('[data-ap-home-category]')];const categories=blocks.map(b=>b.dataset.apHomeCategory).filter(Boolean);const badge=document.querySelector('[data-ap-personalized-badge]');
  if(!state.home.enabled){blocks.forEach(b=>b.hidden=false);if(badge)badge.hidden=true;return;}
  const rank=new Map(ordered(state,categories).map((c,i)=>[c,i]));const hidden=new Set(state.home.hidden);
  blocks.sort((a,b)=>(rank.get(a.dataset.apHomeCategory)??999)-(rank.get(b.dataset.apHomeCategory)??999)).forEach(block=>{block.hidden=hidden.has(block.dataset.apHomeCategory);host.append(block);});if(badge)badge.hidden=false;
}
export function initGlobal(){
  syncSaved();syncTopics();applyHome();
  document.addEventListener('click',event=>{const target=event.target instanceof Element?event.target:null;if(!target)return;const card=target.closest('[data-ap-save]');if(card){if(card.dataset.slug)toggleSaved(card.dataset.slug);return;}const article=target.closest('[data-save-article]');if(article){const slug=article.closest('[data-plus-actions]')?.dataset.slug;if(slug)toggleSaved(slug);return;}const follow=target.closest('[data-follow-topic]');if(follow){const picker=follow.closest('[data-plus-actions]')?.querySelector('[data-topic-picker]');if(picker)picker.hidden=!picker.hidden;return;}const topic=target.closest('[data-topic]');if(topic){const value=topic.dataset.topic;if(!value)return;const state=read();state.topics=toggle(state.topics,value);write(state);}});
  window.addEventListener('apurantepluschange',event=>{syncSaved(event.detail);syncTopics(event.detail);applyHome(event.detail);});
  window.addEventListener('storage',event=>{if(event.key===STORAGE_KEY){syncSaved();syncTopics();applyHome();}});
}
