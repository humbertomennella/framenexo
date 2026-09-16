import {test,expect} from '@playwright/test';

test('barra superior comunica monitoramento sem prometer horário de publicação',async({page})=>{
  await page.goto('./');
  const notice=page.locator('[data-edition-notice]');
  await expect(notice).toBeVisible();
  await expect(notice).toContainText('Monitoramento contínuo');
  await expect(notice).toContainText('Novas matérias entram após verificação editorial');
  await expect(notice).not.toContainText('08h');
  await expect(notice).not.toContainText('13h');
  await expect(notice).not.toContainText('18h');
  await expect(notice).not.toContainText('22h');
  await expect(notice.locator('[data-next-edition]')).toHaveCount(0);
  await expect(page.locator('[data-edition-schedule]')).toHaveCount(0);

  await notice.locator('[data-edition-open]').click();
  const dialog=page.locator('[data-edition-dialog]');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('heading',{name:'O APURANTE publica quando a apuração sustenta a matéria.'})).toBeVisible();
  await expect(dialog).toContainText('Monitoramento contínuo');
  await expect(dialog).toContainText('Verificação antes de publicar');
  await expect(dialog).toContainText('Sem preencher espaço');
  await expect(dialog).toContainText('Não prometemos quantidade nem horário exato de publicação.');
  await expect(dialog).toContainText('Fatos urgentes');
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
  expect(box.height).toBeLessThanOrEqual(40);
  expect(box.width).toBeLessThanOrEqual(390);
  await expect(page.locator('[data-edition-schedule]')).toHaveCount(0);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('arquivo explica agrupamento pelas quatro janelas e preserva publicações anteriores',async({page})=>{
  await page.goto('./arquivo/');
  await expect(page.getByRole('heading',{name:'Arquivo',exact:true})).toBeVisible();
  await expect(page.getByText(/08h, 13h, 18h e 22h/).last()).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toContainText(/ARQUIVO ANTERIOR|EDIÇÃO PROGRAMADA|EDIÇÃO EXTRAORDINÁRIA/);
});
