import {test,expect} from '@playwright/test';

test('Home explains the four daily editions without polling',async({page})=>{
  await page.goto('./');
  const schedule=page.locator('[data-edition-schedule]');
  await expect(schedule).toBeVisible();
  await expect(schedule).toContainText('EDIÇÕES PROGRAMADAS');
  await expect(schedule).toContainText('08h · 13h · 18h · 22h');
  await expect(schedule).toContainText('Notícias urgentes podem gerar uma edição extraordinária');
  await expect(schedule.locator('[data-next-edition]')).not.toHaveText('Calculando…');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('schedule remains compact on a 390px viewport',async({page})=>{
  await page.setViewportSize({width:390,height:800});
  await page.goto('./');
  const schedule=page.locator('[data-edition-schedule]');
  await expect(schedule).toBeVisible();
  expect(await schedule.evaluate(el=>el.getBoundingClientRect().width)).toBeLessThanOrEqual(390);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('archive explains edition grouping and preserves legacy publications',async({page})=>{
  await page.goto('./arquivo/');
  await expect(page.getByRole('heading',{name:'Arquivo',exact:true})).toBeVisible();
  await expect(page.getByText(/agrupadas pelas edições de 08h, 13h, 18h e 22h/)).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toContainText(/ARQUIVO ANTERIOR|EDIÇÃO PROGRAMADA|EDIÇÃO EXTRAORDINÁRIA/);
});
