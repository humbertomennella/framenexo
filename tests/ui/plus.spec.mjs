import {test,expect} from '@playwright/test';

test('APURANTE+ salva nos cards e personaliza a Home via localStorage',async({page,context})=>{
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('./');
  const save=page.locator('[data-ap-save]').first();
  await expect(save).toBeVisible();
  await save.click();
  await expect(save).toHaveAttribute('aria-pressed','true');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante-plus-v1')));
  expect(state.saved).toHaveLength(1);
  expect(await context.cookies()).toHaveLength(0);

  await page.goto('./meu-apurante/');
  await expect(page.locator('[data-ap-saved-list] .ap-saved-item')).toHaveCount(1);
  await page.locator('[data-ap-preferred-categories] input[type=checkbox]').first().check();
  await page.locator('[data-ap-home-enabled]').check();
  await page.locator('[data-ap-home-categories] input[type=checkbox]').first().uncheck();

  await page.goto('./');
  await expect(page.locator('[data-ap-personalized-badge]')).toBeVisible();
  await expect(page.locator('[data-ap-home-category][hidden]')).toHaveCount(1);
  expect(errors).toEqual([]);
});

test('APURANTE+ exporta e importa configuração JSON',async({page})=>{
  await page.goto('./meu-apurante/');
  const downloadPromise=page.waitForEvent('download');
  await page.locator('[data-ap-export]').click();
  const download=await downloadPromise;
  expect(download.suggestedFilename()).toBe('apurante-plus-config.json');

  const payload={app:'APURANTE+',schemaVersion:1,state:{categories:['Tecnologia'],topics:['IA'],saved:[],home:{enabled:true,order:['Tecnologia'],hidden:[]}}};
  await page.locator('[data-ap-import]').setInputFiles({name:'apurante-plus-config.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(payload))});
  await expect(page.locator('[data-ap-status]')).toContainText('importadas com sucesso');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante-plus-v1')));
  expect(state.categories).toContain('Tecnologia');
  expect(state.topics).toContain('IA');
  expect(state.home.enabled).toBe(true);
});

test('ações do APURANTE+ continuam funcionando dentro da matéria',async({page})=>{
  await page.goto('./ultimas/');
  await page.locator('a[href*="/noticias/"]').first().click();
  const save=page.locator('[data-save-article]');
  await expect(save).toHaveText('Salvar matéria');
  await save.click();
  await expect(save).toHaveAttribute('aria-pressed','true');
  await expect(save).toHaveText('Salva ✓');
  await page.locator('[data-follow-topic]').click();
  const topic=page.locator('[data-topic]').first();
  await expect(topic).toBeVisible();
  await topic.click();
  await expect(topic).toHaveAttribute('aria-pressed','true');
});
