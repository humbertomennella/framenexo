import {test,expect} from '@playwright/test';

test('barra superior mostra a frequência horária e abre a explicação',async({page})=>{
  await page.goto('./');
  const notice=page.locator('[data-edition-notice]');
  await expect(notice).toBeVisible();
  await expect(notice).toContainText('a cada hora');
  await expect(notice.locator('[data-next-edition]')).not.toHaveText('calculando…');
  await expect(page.locator('[data-edition-schedule]')).toHaveCount(0);

  await notice.locator('[data-edition-open]').click();
  const dialog=page.locator('[data-edition-dialog]');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('heading',{name:'O APURANTE fecha notícias de hora em hora.'})).toBeVisible();
  await expect(dialog).toContainText('Uma janela por hora');
  await expect(dialog).toContainText('edição extraordinária');
  await expect(dialog).toContainText('janela horária nunca vira desculpa para preencher espaço com notícia fraca');
  await dialog.getByRole('button',{name:'Entendi'}).click();
  await expect(dialog).not.toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('barra de edições ocupa pouco espaço em 390px',async({page})=>{
  await page.setViewportSize({width:390,height:800});
  await page.goto('./');
  const notice=page.locator('[data-edition-notice]');
  await expect(notice).toBeVisible();
  const box=await notice.boundingBox();
  expect(box.height).toBeLessThanOrEqual(36);
  expect(box.width).toBeLessThanOrEqual(390);
  await expect(page.locator('[data-edition-schedule]')).toHaveCount(0);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('arquivo explica agrupamento por janela horária e preserva publicações anteriores',async({page})=>{
  await page.goto('./arquivo/');
  await expect(page.getByRole('heading',{name:'Arquivo',exact:true})).toBeVisible();
  await expect(page.getByText(/agrupadas por janelas editoriais horárias/)).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toContainText(/ARQUIVO ANTERIOR|EDIÇÃO PROGRAMADA|EDIÇÃO EXTRAORDINÁRIA/);
});
