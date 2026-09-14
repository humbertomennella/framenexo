import schedule from '../../data/edition-schedule.json';
import type {Article} from './news';

export const editionSchedule=schedule;
export const editionHours=[...schedule.slots].sort((a,b)=>a-b);
export const editionHoursLabel=editionHours.map(hour=>`${String(hour).padStart(2,'0')}h`).join(' · ');

export const editionTitle=(article?:Article|null)=>{
 if(!article)return 'Cronograma editorial';
 if(article.editionLabel)return article.editionLabel;
 return 'Publicação anterior ao cronograma';
};

export const editionKey=(article:Article)=>article.editionId||`legacy:${article.publishedAt.slice(0,10)}`;

const normalizedEditionSlot=(article:Article)=>{
 const slot=article.editionSlot;
 if(!slot)return article.publishedAt;
 if(/^\d{2}:\d{2}$/.test(slot))return `${article.publishedAt.slice(0,10)}T${slot}:00-03:00`;
 return slot;
};

export interface EditionGroup {key:string;type:'scheduled'|'extraordinary'|'legacy';slot:string;label:string;items:Article[]}

export const groupByEdition=(items:Article[]):EditionGroup[]=>{
 const groups=new Map<string,EditionGroup>();
 for(const article of items){
  const key=editionKey(article);
  let group=groups.get(key);
  if(!group){
   const type=article.editionType||'legacy';
   group={key,type,slot:normalizedEditionSlot(article),label:article.editionLabel||(type==='legacy'?'Publicações anteriores ao cronograma':'Edição'),items:[]};
   groups.set(key,group);
  }
  group.items.push(article);
 }
 return [...groups.values()].sort((a,b)=>b.slot.localeCompare(a.slot));
};
