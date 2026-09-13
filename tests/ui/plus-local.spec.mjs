import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./');
  await page.evaluate(()=>localStorage.removeItem('apurante_plus'));
  await page.reload();
});

test('cards save articles using only localStorage',async({page,context})=>{
  const button=page.locator('.card [data-plus-save]').first();
  await expect(button).toBeVisible();
  const slug=await button.getAttribute('data-plus-save');
  await button.click();
  await expect(button).toHaveAttribute('aria-pressed','true');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.savedArticles).toContain(slug);
  expect(await context.cookies()).toHaveLength(0);
});

test('Meu APURANTE controls Home visibility and order locally',async({page})=>{
  await page.goto('./meu-apurante/');
  await page.locator('[data-home-enabled]').check();
  const first=page.locator('[data-home-row]').first();
  const category=await first.getAttribute('data-category');
  await first.locator('[data-home-visible]').uncheck();
  await first.locator('[data-home-down]').click();
  await page.goto('./');
  await expect(page.locator('[data-plus-home-badge]')).toBeVisible();
  await expect(page.locator(`[data-home-category="${category}"]`)).toBeHidden();
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.preferences.home.enabled).toBe(true);
  expect(state.preferences.home.hiddenCategories).toContain(category);
});

test('APURANTE+ exports and imports portable JSON settings',async({page})=>{
  await page.goto('./meu-apurante/');
  const downloadPromise=page.waitForEvent('download');
  await page.locator('[data-plus-export]').click();
  const download=await downloadPromise;
  expect(download.suggestedFilename()).toBe('apurante-plus-config.json');
  const payload={app:'APURANTE+',schemaVersion:1,state:{version:1,interests:['Tecnologia'],savedArticles:[],followedTopics:['IA'],preferences:{compactFeed:false,home:{enabled:true,order:['Tecnologia'],hiddenCategories:[]}}}};
  await page.locator('[data-plus-import]').setInputFiles({name:'apurante-plus-config.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(payload))});
  await expect(page.locator('[data-plus-portability-feedback]')).toContainText('importadas com sucesso');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.interests).toContain('Tecnologia');
  expect(state.followedTopics).toContain('IA');
  expect(state.preferences.home.enabled).toBe(true);
});
