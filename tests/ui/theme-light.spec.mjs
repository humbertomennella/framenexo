import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./');
  await page.evaluate(()=>localStorage.removeItem('apurante_theme'));
  await page.reload();
});

const expectOnlyLight=scheme=>expect(scheme.trim().split(/\s+/).sort()).toEqual(['light','only']);
const rgb=s=>s.match(/\d+/g).slice(0,3).map(Number);
const luminance=values=>{
  const [r,g,b]=values.map(v=>{const c=v/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4});
  return .2126*r+.7152*g+.0722*b;
};
const contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};

test('light theme uses the editorial paper palette and readable link contrast',async({page})=>{
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  const colors=await page.evaluate(()=>({
    body:getComputedStyle(document.body).backgroundColor,
    text:getComputedStyle(document.body).color
  }));
  expect(colors.body).toBe('rgb(244, 243, 239)');
  expect(colors.text).toBe('rgb(21, 24, 26)');
  const link=page.locator('.lead-read').first();
  await link.hover();
  const linkColor=await link.evaluate(el=>getComputedStyle(el).color);
  expect(contrast(rgb(linkColor),rgb(colors.body))).toBeGreaterThanOrEqual(4.5);
});

test('light theme resists forced-dark behavior and persists on a 390px mobile viewport',async({page})=>{
  await page.emulateMedia({colorScheme:'dark'});
  await page.setViewportSize({width:390,height:800});
  const toggle=page.locator('[data-theme-toggle]');
  await expect(toggle).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  await expect(page.locator('body')).toHaveAttribute('data-theme','light');
  await expect(page.locator('meta[name="color-scheme"]')).toHaveAttribute('content','only light');
  await toggle.click();
  await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
  await toggle.click();
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  await expect.poll(()=>page.locator('.site-header').evaluate(el=>getComputedStyle(el).backgroundColor)).toBe('rgb(247, 247, 243)');
  const state=await page.evaluate(()=>({
    body:getComputedStyle(document.body).backgroundColor,
    htmlScheme:document.documentElement.style.colorScheme,
    bodyScheme:document.body.style.colorScheme,
    stored:localStorage.getItem('apurante_theme')
  }));
  expect(state.body).toBe('rgb(244, 243, 239)');
  expectOnlyLight(state.htmlScheme);
  expectOnlyLight(state.bodyScheme);
  expect(state.stored).toBe('light');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  await expect(page.locator('meta[name="color-scheme"]')).toHaveAttribute('content','only light');
  const persisted=await page.evaluate(()=>({
    body:getComputedStyle(document.body).backgroundColor,
    htmlScheme:document.documentElement.style.colorScheme,
    bodyScheme:document.body.style.colorScheme
  }));
  expect(persisted.body).toBe('rgb(244, 243, 239)');
  expectOnlyLight(persisted.htmlScheme);
  expectOnlyLight(persisted.bodyScheme);
});

test('theme metadata follows the manual choice instead of system preference',async({page})=>{
  await page.emulateMedia({colorScheme:'dark'});
  const schemeMeta=page.locator('meta[name="color-scheme"]');
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  await expect(schemeMeta).toHaveAttribute('content','only light');
  await page.locator('[data-theme-toggle]').click();
  await expect(schemeMeta).toHaveAttribute('content','dark');
  await page.locator('[data-theme-toggle]').click();
  await expect(schemeMeta).toHaveAttribute('content','only light');
});

test('APURANTE+ header wordmark stays visible and opens the explainer',async({page})=>{
  const plus=page.getByRole('link',{name:'Conhecer o APURANTE+'});
  await expect(plus).toBeVisible();
  await expect(plus).toContainText('APURANTE+');
  await expect(plus).toHaveAttribute('href',/mais\/$/);
});

test('Home keeps one dominant lead and restores an image-led focus carousel',async({page})=>{
  await expect(page.locator('.lead-story')).toBeVisible();
  await expect(page.locator('.lead-story h2 a')).toBeVisible();
  await expect(page.locator('.lead-media img')).toBeVisible();
  const carousel=page.locator('.focus-carousel-rail [data-headlines]');
  await expect(carousel).toBeVisible();
  const slideCount=await carousel.locator('[data-slide]').count();
  expect(slideCount).toBeGreaterThanOrEqual(3);
  await expect(carousel.locator('.headline-slide.is-current .headline-photo img')).toBeVisible();
  const before=await carousel.locator('[data-position]').textContent();
  await carousel.locator('[data-next]').click();
  await expect.poll(()=>carousel.locator('[data-position]').textContent()).not.toBe(before);
  await expect(page.locator('.elections-home')).toBeVisible();
  await expect(page.locator('.elections-home [data-election-article]').first()).toBeVisible();
  await expect(page.locator('.edition-promise')).toBeVisible();
  await expect(page.locator('.editoria-block')).toHaveCount(10);
  await expect(page.locator('.front-grid')).toHaveCount(0);
});
