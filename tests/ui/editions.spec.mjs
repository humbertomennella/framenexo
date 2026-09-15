import {test,expect} from '@playwright/test';

test('barra superior mostra as quatro janelas e abre a explicação',async({page})=>{
  await page.goto('./');
  const notice=page.locator('[data-edition-notice]');
  await expect(notice).toBeVisible();
  await expect(notice).toContainText('08h');
  await expect(notice).toContainText('13h');
  await expect(notice).toContainText('18h');
  await expect(notice).toContainText('22h');
  await expect(notice.locator('[data-next-edition]')).not.toHaveText('calculando…');
  await expect(notice.locator('[data-next-edition]')).toHaveText(/(?:08|13|18|22):(07|27) (?:hoje|amanhã)/);
  await expect(page.locator('[data-edition-schedule]')).toHaveCount(0);

  await notice.locator('[data-edition-open]').click();
  const dialog=page.locator('[data-edition-dialog]');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('heading',{name:'O APURANTE fecha quatro edições regulares por dia.'})).toBeVisible();
  await expect(dialog).toContainText('Quatro janelas editoriais');
  await expect(dialog).toContainText('20 matérias');
  await expect(dialog).toContainText('duas para cada uma das dez editorias');
  await expect(dialog).toContainText('edição extraordinária');
  await expect(dialog).toContainText('meta editorial nunca vira desculpa para preencher espaço com notícia fraca');
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
  await expect(page.getByText(/08h, 13h, 18h e 22h/)).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toBeVisible();
  await expect(page.locator('.archive-edition').first()).toContainText(/ARQUIVO ANTERIOR|EDIÇÃO PROGRAMADA|EDIÇÃO EXTRAORDINÁRIA/);
});
