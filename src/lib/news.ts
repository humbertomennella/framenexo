import {href} from './paths';
export {href};
export const categories = ['Brasil','Mundo','Política','Economia','Tecnologia','Ciência','Cultura','Esportes','Saúde','Meio Ambiente'];
export const categorySlug = (s:string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,'-');
export interface Article {
 title:string; slug:string; description:string; publishedAt:string; updatedAt:string; category:string; tags:string[]; quickTakeaways?:string[];
 image:string; imageAlt:string; imageCredit:string; status:string; confidence:string; relevance:number; eventKey:string;
 sources:{name:string;url:string;publishedAt:string;type:string}[]; corrections?:{date:string;text:string}[]; body:string; Content:any;
}
const modules = import.meta.glob('../../content/news/*.md', {eager:true}) as Record<string,any>;
export const articles:Article[] = Object.values(modules).map(m=>({...m.frontmatter, Content:m.Content, body:m.rawContent()})).filter(a=>a.status==='published').sort((a,b)=>b.publishedAt.localeCompare(a.publishedAt) || b.relevance-a.relevance);
export const articleUrl = (a:Article) => href(`noticias/${a.slug}/`);
const genericEditorialImages = new Set(['/og.png','/images/cathedral.webp']);
export const usesEditorialCover = (a:Article) => genericEditorialImages.has(a.image);
export const inCategory = (a:Article,c:string) => a.category===c || a.tags.includes(c);
export const date = (s:string) => new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',year:'numeric',timeZone:s.length===10?'UTC':'America/Sao_Paulo'}).format(new Date(s));
export const time = (s:string) => new Intl.DateTimeFormat('pt-BR',{hour:'2-digit',minute:'2-digit',timeZone:'America/Sao_Paulo'}).format(new Date(s));
export const reading = (a:Article) => Math.max(2,Math.ceil(a.body.split(/\s+/).length/180));
export const jsonld = (x:unknown) => JSON.stringify(x).replace(/</g,'\\u003c');
