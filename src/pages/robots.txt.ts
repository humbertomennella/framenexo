import {href} from '../lib/paths';
export function GET({site}:{site:URL}){return new Response(`User-agent: *\nAllow: /\nSitemap: ${new URL(href('sitemap.xml'),site).href}\n`,{headers:{'Content-Type':'text/plain; charset=utf-8'}})}
