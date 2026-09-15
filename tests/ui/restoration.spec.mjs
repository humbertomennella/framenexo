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
