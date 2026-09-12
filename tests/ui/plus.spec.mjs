import {test,expect} from '@playwright/test';

test('APURANTE+ stores preferences and saved stories locally',async({page})=>{
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('./mais/');
  await expect(page.getByRole('heading',{name:'Informação organizada para você.'})).toBeVisible();
  const tecnologia=page.getByRole('button',{name:'Tecnologia',exact:true});
  await tecnologia.click();
  await expect(tecnologia).toHaveAttribute('aria-pressed','true');
  await expect(page.locator('[data-plus-feed] article').first()).toBeVisible();
  await page.goto('./ultimas/');
  await page.locator('a[href*="/noticias/"]').first().click();
  const save=page.locator('[data-save-article]');
  await expect(save).toHaveText('Salvar matéria');
  await save.click();
  await expect(save).toHaveAttribute('aria-pressed','true');
  await expect(save).toHaveText('Salva ✓');
  await page.goto('./mais/');
  await expect(page.locator('[data-saved-feed] article')).toHaveCount(1);
  expect(errors).toEqual([]);
});
