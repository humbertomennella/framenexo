import {href} from './paths';
export {href};
export const categories = ['Brasil','Mundo','Política','Economia','Tecnologia','Ciência','Cultura','Esportes','Saúde','Meio Ambiente'];
export const categorySlug = (s:string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,'-');
export interface Article {
 timeline?:{date:string;text:string;sourceURL:string}[]; format?:string; historicalReview?:string; electionCoverage?:boolean; articleId:string; title:string; slug:string; description:string; publishedAt:string; updatedAt:string; category:string; tags:string[]; quickTakeaways?:string[];
 editionId?:string; editionType?:'scheduled'|'extraordinary'; editionSlot?:string; editionLabel?:string;
 image:string; imageAlt:string; imageCredit:string; status:string; confidence:string; relevance:number; eventKey:string;
 sources:{name:string;url:string;publishedAt:string;type:string;organization?:string;originalOrganization?:string;role?:string}[]; verificationPolicyVersion?:number; leadSourceOrganization?:string; corrections?:{date:string;text:string}[]; body:string; Content:any;
}
const modules = import.meta.glob('../../content/news/*.md', {eager:true}) as Record<string,any>;
const stableHash=(value:string)=>{let hash=2166136261;for(let i=0;i<value.length;i++){hash^=value.charCodeAt(i);hash=Math.imul(hash,16777619)}return (hash>>>0).toString(36).padStart(7,'0').slice(0,7)};
const legacyArticleId=(a:any)=>`apr-${String(a.publishedAt||'legacy').slice(0,10)}-${stableHash(String(a.eventKey||a.slug||a.title||'article'))}`;
const editorialImageOverrides:Record<string,{image:string;imageAlt:string;imageCredit:string}>={
 'chuvas-vale-do-ribeira-152-familias-abrigos':{
  image:'/images/news/temporais-sao-paulo-alerta-editorial.webp',
  imageAlt:'Ilustração editorial temática de temporais, chuva intensa e alagamentos. Não é fotografia do episódio no Vale do Ribeira.',
  imageCredit:'Apurante Editorial · Imagem editorial temática do acervo visual; não é fotografia do acontecimento.'
 },
 'sus-pneumo-20-maiores-85-anos':{
  image:'/images/news/vacina-meningococica-seis-semanas-editorial.webp',
  imageAlt:'Ilustração editorial temática de vacinação e proteção em saúde. Não representa paciente, dose ou aplicação real da Pneumo 20.',
  imageCredit:'Apurante Editorial · Imagem editorial temática do acervo visual; não é fotografia do acontecimento.'
 },
 'move-brasil-r-30-bilhoes-financiamento-veiculos':{
  image:'/images/news/brasil-tem-2-milhoes-de-pessoas-que-trabalham-por-meio-de-aplicativos.webp',
  imageAlt:'Ilustração editorial temática de trabalhadores por aplicativo e mobilidade urbana, usada para representar o público do Move Brasil. Não retrata beneficiário real.',
  imageCredit:'Apurante Editorial · Imagem editorial temática do acervo visual; não é fotografia do acontecimento.'
 },
 'stf-analisa-abertura-investigacao-moraes-vorcaro':{
  image:'/images/news/stf-pf-crise-institucional-editorial.webp',
  imageAlt:'Ilustração editorial institucional sobre STF, investigação e tensão entre instituições. Não retrata pessoas nem material real da investigação.',
  imageCredit:'Apurante Editorial · Imagem editorial temática do acervo visual; não é fotografia do acontecimento.'
 }
};
export const articles:Article[] = Object.values(modules).map(m=>{const raw={...m.frontmatter,Content:m.Content,body:m.rawContent()};const override=editorialImageOverrides[raw.slug];return {...raw,articleId:raw.articleId||legacyArticleId(raw),...(override||{})}}).filter(a=>a.status==='published').sort((a,b)=>Date.parse(b.publishedAt)-Date.parse(a.publishedAt) || b.relevance-a.relevance);
export const articleUrl = (a:Article) => href(`noticias/${a.slug}/`);
const genericEditorialImages = new Set(['/og.png','/images/cathedral.webp']);
export const usesEditorialCover = (a:Article) => genericEditorialImages.has(a.image);
export const inCategory = (a:Article,c:string) => a.category===c || a.tags.includes(c);
export const date = (s:string) => new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',year:'numeric',timeZone:s.length===10?'UTC':'America/Sao_Paulo'}).format(new Date(s));
export const time = (s:string) => new Intl.DateTimeFormat('pt-BR',{hour:'2-digit',minute:'2-digit',timeZone:'America/Sao_Paulo'}).format(new Date(s));
export const reading = (a:Article) => Math.max(1,Math.ceil(a.body.replace(/https?:\/\/\S+/g,'').replace(/[#*_>`]/g,'').trim().split(/\s+/).length/220));
export const independentSourceCount = (a:Article) => new Set(a.sources.map(s=>s.originalOrganization||s.organization||(()=>{try{return new URL(s.url).hostname}catch{return s.name}})())).size;
export const displayedConfidence = (a:Article) => independentSourceCount(a)<2?'RELATO':a.confidence;
export const jsonld = (x:unknown) => JSON.stringify(x).replace(/</g,'\\u003c');
