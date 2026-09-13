import {test,expect} from '@playwright/test';

test('high contrast overrides the light palette instead of falling back to dark',async({page})=>{
  await page.goto('./');
  await page.locator('[data-theme-toggle]').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme','light');
  await page.locator('.cards a').first().click();
  await page.getByText('Ajustar leitura',{exact:true}).click();
  await page.getByRole('button',{name:'Alto contraste'}).click();
  await expect(page.locator('html')).toHaveClass(/reading-contrast/);
  const colors=await page.evaluate(()=>({
    body:getComputedStyle(document.body).backgroundColor,
    text:getComputedStyle(document.body).color
  }));
  expect(colors.body).toBe('rgb(255, 255, 255)');
  expect(colors.text).toBe('rgb(0, 0, 0)');
});
