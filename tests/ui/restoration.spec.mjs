import {test,expect} from '@playwright/test';

test('election panel refreshes published data without reloading unchanged slides',async({page})=>{
 await page.clock.install();
 await page.goto('./eleicoes/');
 await page.waitForLoadState('networkidle');
 let requests=0;
 await page.route('**/eleicoes/',async route=>{requests++;await route.continue();});
 await page.clock.fastForward(60010);
 await expect.poll(()=>requests).toBeGreaterThan(0);
 await page.waitForLoadState('networkidle');
 expect(requests).toBe(1);
});

test('urgent panel contains only explicitly urgent stories',async({page})=>{
 await page.goto('./');
 const panel=page.locator('[data-headlines][data-moment]');
 if(await panel.count()){
  await expect(panel.locator('[data-slide]:not([data-level="urgent"])')).toHaveCount(0);
 }
});

test('home urgent strip receives new alerts and expires them without navigation',async({page})=>{
 await page.clock.install();
 await page.goto('./');
 const strip=page.locator('[data-urgent-strip]');
 await expect(strip).toBeVisible();
 const start=await page.evaluate(()=>Date.now());
 const items=[{title:'Alerta de teste com validade explícita',url:'/noticias/teste/',expiresAt:new Date(start+90000).toISOString()}];
 const encoded=JSON.stringify(items).replaceAll('&','&amp;').replaceAll('"','&quot;');
 await page.route('**/',route=>route.fulfill({contentType:'text/html',body:`<aside data-urgent-strip data-items="${encoded}"></aside>`}));
 await page.clock.fastForward(60010);
 await expect(strip).toContainText(items[0].title);
 await page.clock.fastForward(30020);
 await expect(strip).toContainText('Nenhum alerta urgente verificado vigente.');
});
