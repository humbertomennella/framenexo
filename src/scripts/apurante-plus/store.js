export const STORAGE_KEY='apurante-plus-v1';
const ALT_KEY='apurante-plus:v1';
export const VERSION=1;
const list=value=>Array.isArray(value)?[...new Set(value.filter(v=>typeof v==='string').map(v=>v.trim()).filter(Boolean))]:[];
export const emptyState=()=>({version:VERSION,categories:[],topics:[],saved:[],home:{enabled:false,order:[],hidden:[]},updatedAt:null});
export function normalize(value){
  const source=value&&typeof value==='object'?value:{};
  const home=source.home&&typeof source.home==='object'?source.home:{};
  return {version:VERSION,categories:list(source.categories??source.preferredCategories),topics:list(source.topics??source.followedTags),saved:list(source.saved??source.savedArticles),home:{enabled:Boolean(home.enabled),order:list(home.order),hidden:list(home.hidden)},updatedAt:typeof source.updatedAt==='string'?source.updatedAt:null};
}
export function read(){
  try{const raw=localStorage.getItem(STORAGE_KEY)??localStorage.getItem(ALT_KEY);return raw?normalize(JSON.parse(raw)):emptyState();}catch{return emptyState();}
}
export function write(next){
  const state=normalize({...next,updatedAt:new Date().toISOString()});
  localStorage.setItem(STORAGE_KEY,JSON.stringify(state));
  if(localStorage.getItem(ALT_KEY)!==null)localStorage.removeItem(ALT_KEY);
  window.dispatchEvent(new CustomEvent('apurantepluschange',{detail:state}));
  return state;
}
export function toggle(values,value,force){
  const set=new Set(values);const add=typeof force==='boolean'?force:!set.has(value);if(add)set.add(value);else set.delete(value);return [...set];
}
export function toggleSaved(slug,force){const state=read();state.saved=toggle(state.saved,slug,force);return write(state);}
export function clear(){localStorage.removeItem(STORAGE_KEY);localStorage.removeItem(ALT_KEY);window.dispatchEvent(new CustomEvent('apurantepluschange',{detail:emptyState()}));}
