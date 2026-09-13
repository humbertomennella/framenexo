import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./');
  await page.evaluate(()=>localStorage.removeItem('apurante_theme'));
  await page.reload();
});

test('light theme uses the editorial paper palette and readable hover contrast',async({page})=>{
  await page.locator('[data-theme-toggle]').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  const colors=await page.evaluate(()=>({
    body:getComputedStyle(document.body).backgroundColor,
    text:getComputedStyle(document.body).color
  }));
  expect(colors.body).toBe('rgb(244, 243, 239)');
  expect(colors.text).toBe('rgb(32, 33, 36)');
  const link=page.locator('.editoria-links a').first();
  await link.hover();
  expect(await link.evaluate(el=>getComputedStyle(el).color)).toBe('rgb(45, 80, 16)');
});

test('APURANTE+ header wordmark stays visible and opens the explainer',async({page})=>{
  const plus=page.getByRole('link',{name:'Conhecer o APURANTE+'});
  await expect(plus).toBeVisible();
  await expect(plus).toContainText('APURANTE+');
  await expect(plus).toHaveAttribute('href',/mais\/$/);
});

test('Home keeps election panel before the urgent radar and both have content',async({page})=>{
  const panels=page.locator('.front-grid > section');
  await expect(panels.nth(0)).toHaveAttribute('aria-label','Em foco');
  await expect(panels.nth(1)).toHaveAttribute('aria-label','ELEIÇÕES 2026');
  await expect(panels.nth(2)).toHaveAttribute('aria-label','URGENTE');
  await expect(panels.nth(1).locator('[data-election-article]').first()).toBeVisible();
  await expect(panels.nth(2).locator('[data-slide]').first()).toBeVisible();
});
