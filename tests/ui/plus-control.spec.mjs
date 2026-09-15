import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./');
  await page.evaluate(()=>localStorage.removeItem('apurante_plus'));
  await page.reload();
});

test('favorite editorias reorder Home and activate personal feed',async({page})=>{
  await page.goto('./meu-apurante/');
  const interests=page.locator('[data-interest-selector]');
  await interests.getByLabel('Tecnologia').check();
  await interests.getByRole('button',{name:'Aplicar ao meu APURANTE+'}).click();
  await page.goto('./');
  await expect(page.locator('[data-home-plus]')).toBeVisible();
  await expect(page.locator('[data-plus-interest-count]')).toHaveText('1');
  await expect(page.locator('[data-plus-personal-block]')).toBeVisible();
  const firstCategory=await page.locator('[data-home-sections] > [data-home-category]').first().getAttribute('data-home-category');
  expect(firstCategory).toBe('Tecnologia');
});

test('saved stories become a Ler depois shelf on Home',async({page})=>{
  const save=page.locator('.latest-grid .card [data-plus-save]').first();
  await expect(save).toBeVisible();
  await save.click();
  await expect(page.locator('[data-home-plus]')).toBeVisible();
  await expect(page.locator('[data-plus-saved-count]')).toHaveText('1');
  await expect(page.locator('[data-plus-saved-block]')).toBeVisible();
  await expect(page.locator('[data-plus-home-saved]:not([hidden])')).toHaveCount(1);
});

test('Meu APURANTE+ controls shelves, order and compact mode',async({page})=>{
  await page.goto('./meu-apurante/');
  await page.locator('[data-home-enabled]').check();
  await page.locator('[data-compact-feed]').check();
  await page.locator('[data-home-personal-feed]').uncheck();
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.version).toBe(3);
  expect(state.preferences.home.enabled).toBe(true);
  expect(state.preferences.compactFeed).toBe(true);
  expect(state.preferences.home.showPersonalFeed).toBe(false);
  await page.goto('./');
  await expect(page.locator('html')).toHaveClass(/plus-compact-home/);
  await expect(page.locator('[data-plus-home-badge]')).toBeVisible();
});

test('APURANTE+ landing states simple local ownership model',async({page})=>{
  await page.goto('./mais/');
  await expect(page.getByText('Jornalismo independente · Gratuito e local')).toBeVisible();
  await expect(page.getByRole('heading',{name:'O portal é público. O seu APURANTE+ é só seu.'})).toBeVisible();
  await expect(page.getByText('Sem assinatura',{exact:true})).toBeVisible();
  await expect(page.getByText('Sem paywall',{exact:true})).toBeVisible();
  await expect(page.getByText('Sem cadastro',{exact:true})).toBeVisible();
  await expect(page.getByRole('link',{name:'Abrir Meu APURANTE+'})).toBeVisible();
});
