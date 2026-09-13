import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./mais/');
  await page.evaluate(()=>localStorage.removeItem('apurante_plus'));
  await page.reload();
});

test('interests, saved articles and followed topics persist locally',async({page})=>{
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await expect(page.getByRole('link',{name:'Abrir Meu APURANTE+'}).first()).toBeVisible();
  await page.getByLabel('Tecnologia').check();
  await page.getByLabel('Ciência').check();
  await page.getByRole('button',{name:'Aplicar ao meu APURANTE+'}).click();
  await expect(page.getByRole('status')).toContainText('influenciam sua Home');
  await page.reload();
  await expect(page.getByLabel('Tecnologia')).toBeChecked();
  await expect(page.getByLabel('Ciência')).toBeChecked();

  await page.goto('./');
  const articleLink=page.locator('section.headlines h3 a').first();
  const title=(await articleLink.textContent())?.trim();
  await articleLink.click();
  const save=page.locator('[data-plus-save]').first();
  await save.click();
  await expect(save).toHaveAttribute('aria-pressed','true');
  await page.reload();
  await expect(page.locator('[data-plus-save]').first()).toHaveAttribute('aria-pressed','true');

  const follow=page.locator('[data-plus-follow]').first();
  const topic=await follow.getAttribute('data-plus-follow');
  await follow.click();
  await expect(follow).toHaveAttribute('aria-pressed','true');
  await page.reload();
  await expect(page.locator(`[data-plus-follow="${topic}"]`).first()).toHaveAttribute('aria-pressed','true');

  await page.goto('./meu-apurante/');
  await expect(page.locator('[data-saved-article]:not([hidden])')).toHaveCount(1);
  if(title)await expect(page.locator('[data-saved-article]:not([hidden]) h3')).toContainText(title);
  await expect(page.getByRole('button',{name:`Deixar de acompanhar ${topic}`})).toBeVisible();
  await page.getByRole('button',{name:'Remover dos salvos'}).click();
  await expect(page.getByText('Sua lista de leitura está vazia.')).toBeVisible();
  expect(errors).toEqual([]);
});

test('APURANTE+ remains usable without horizontal overflow on mobile',async({page})=>{
  for(const width of [1440,1366,768,390,360]){
    await page.setViewportSize({width,height:width<=390?800:900});
    for(const route of ['./','./mais/','./meu-apurante/']){
      await page.goto(route);
      await expect(page.getByRole('banner').getByRole('link',{name:'Conhecer o APURANTE+'})).toBeVisible();
      expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${route} overflows at ${width}px`).toBe(true);
    }
  }
});

test('header uses the APURANTE+ wordmark and opens the explainer first',async({page})=>{
  await page.goto('./');
  const shortcut=page.getByRole('banner').getByRole('link',{name:'Conhecer o APURANTE+'});
  await expect(shortcut).toBeVisible();
  await expect(shortcut).toContainText('APURANTE+');
  await expect(page.getByRole('link',{name:'Voltar ao início do APURANTE'})).toHaveText('Início');
  await shortcut.click();
  await expect(page).toHaveURL(/\/mais\/$/);
  await expect(page.getByRole('link',{name:'APURANTE+ — início'})).toHaveText('APURANTE+');
  await page.getByRole('link',{name:'Abrir Meu APURANTE+'}).first().click();
  await expect(page).toHaveURL(/\/meu-apurante\/$/);
  await page.setViewportSize({width:390,height:800});
  const card=page.locator('.personal-feed .card').first();
  await expect(card).toBeVisible();
  expect(await card.evaluate(element=>getComputedStyle(element).display)).toBe('block');
  expect(await card.locator('.card-image').evaluate(element=>Math.round(element.getBoundingClientRect().width))).toBeGreaterThan(300);
});
