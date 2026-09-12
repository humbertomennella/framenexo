import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./mais/');
  await page.evaluate(()=>localStorage.removeItem('apurante_plus'));
  await page.reload();
});

test('interests, saved articles and followed topics persist locally',async({page})=>{
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await expect(page.getByRole('link',{name:'Conhecer o APURANTE+'}).first()).toBeVisible();
  await page.getByLabel('Tecnologia').check();
  await page.getByLabel('Ciência').check();
  await page.getByRole('button',{name:'Salvar interesses'}).click();
  await expect(page.getByRole('status')).toContainText('Interesses salvos');
  await page.reload();
  await expect(page.getByLabel('Tecnologia')).toBeChecked();
  await expect(page.getByLabel('Ciência')).toBeChecked();

  await page.goto('./');
  const articleLink=page.locator('section.headlines h3 a').first();
  const title=(await articleLink.textContent())?.trim();
  await articleLink.click();
  const save=page.getByRole('button',{name:'Salvar',exact:true}).first();
  await save.click();
  await expect(save).toHaveAttribute('aria-pressed','true');
  await page.reload();
  await expect(page.getByRole('button',{name:'Salva',exact:true}).first()).toHaveAttribute('aria-pressed','true');

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
  await expect(page.getByText('Você ainda não salvou nenhuma matéria.')).toBeVisible();
  expect(errors).toEqual([]);
});

test('APURANTE+ remains usable without horizontal overflow on mobile',async({page})=>{
  await page.setViewportSize({width:360,height:800});
  await page.goto('./');
  await expect(page.getByRole('link',{name:'Conhecer o APURANTE+'})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.goto('./mais/');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.goto('./meu-apurante/');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
