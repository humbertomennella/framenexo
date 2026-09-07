import { defineConfig } from 'astro/config';
export default defineConfig({
  site: process.env.SITE_URL || 'https://framenexo.humberto-mennella.chatgpt.site',
  base: process.env.BASE_PATH || '/',
  output: 'static', trailingSlash: 'always', devToolbar: {enabled: false},
  server: {host: '0.0.0.0', port: 4173, allowedHosts: ['terminal.local']},
  markdown: {shikiConfig: {theme: 'github-dark'}}
});
