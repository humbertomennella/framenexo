const normalize=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const terms=['eleicoes 2026','eleicoes','eleicao','tse','justica eleitoral','urna eletronica','registro de candidatura','pesquisa eleitoral','campanha eleitoral','fundo eleitoral','horario eleitoral','primeiro turno','segundo turno','resultado eleitoral'];
export function isElectionArticle(article){
 if(article.electionCoverage===false)return false;
 if(article.electionCoverage===true)return true;
 const tags=(article.tags||[]).map(normalize);
 if(tags.some(tag=>terms.includes(tag)))return true;
 const text=normalize([article.title,article.description,article.category,...tags].filter(Boolean).join(' '));
 return terms.some(term=>text.includes(term));
}
export function selectElections(articles,now=Date.now()){
 return articles.filter(a=>a.status==='published'&&Date.parse(a.publishedAt)<=now&&!['RUMOR','RELATO'].includes(a.confidence)&&isElectionArticle(a))
  .sort((a,b)=>String(b.updatedAt||b.publishedAt).localeCompare(String(a.updatedAt||a.publishedAt))||b.publishedAt.localeCompare(a.publishedAt));
}
