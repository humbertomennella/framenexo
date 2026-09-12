import {articles,articleUrl} from '../lib/news';
export function GET(){return new Response(JSON.stringify(articles.map(a=>({title:a.title,description:a.description,category:a.category,tags:a.tags,keywords:a.body,url:articleUrl(a)}))),{headers:{'Content-Type':'application/json; charset=utf-8'}})}
