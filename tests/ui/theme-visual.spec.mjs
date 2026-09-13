import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./');
  await page.evaluate(()=>{
    localStorage.removeItem('apurante_theme');
    localStorage.removeItem('apurante_plus');
  });
  await page.reload();
});

test('theme toggle persists the selected theme locally',async({page,context})=>{
  const root=page.locator('html');
  const toggle=page.locator('[data-theme-toggle]');
  await expect(root).toHaveAttribute('data-theme','dark');
  await toggle.click();
  await expect(root).toHaveAttribute('data-theme','light');
  await expect(toggle).toHaveAttribute('aria-pressed','true');
  expect(await page.evaluate(()=>localStorage.getItem('apurante_theme'))).toBe('light');
  await page.reload();
  await expect(root).toHaveAttribute('data-theme','light');
  expect(await context.cookies()).toHaveLength(0);
});

test('personalized Home uses the subtle status bar instead of the old promo card',async({page})=>{
  await page.evaluate(()=>localStorage.setItem('apurante_plus',JSON.stringify({
    version:1,
    interests:[],
    savedArticles:[],
    followedTopics:[],
    preferences:{compactFeed:false,home:{enabled:true,order:[],hiddenCategories:[]}}
  })));
  await page.reload();
  await expect(page.locator('[data-plus-home-badge]')).toBeVisible();
  await expect(page.locator('[data-plus-home-badge]')).toContainText('Home organizada pelas preferências deste dispositivo.');
  await expect(page.locator('.plus-home-promo')).toHaveCount(0);
  await expect(page.locator('[data-plus-home-badge] a').first()).toHaveAttribute('href',/meu-apurante\/#preferencias-home$/);
});
