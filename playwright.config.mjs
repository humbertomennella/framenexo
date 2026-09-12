import {defineConfig} from '@playwright/test';
const base=process.env.BASE_PATH||'/';
export default defineConfig({
 testDir:'./tests/ui',timeout:20000,retries:0,workers:1,reporter:'list',
 use:{baseURL:`http://127.0.0.1:4337${base}`,trace:'retain-on-failure'},
 projects:[{name:'desktop',use:{viewport:{width:1366,height:900}}},{name:'mobile',use:{viewport:{width:390,height:844},isMobile:true,hasTouch:true}}],
 webServer:{command:'python3 scripts/serve_dist.py',url:`http://127.0.0.1:4337${base}`,reuseExistingServer:false,timeout:30000}
});
