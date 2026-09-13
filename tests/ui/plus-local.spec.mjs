import {test,expect} from '@playwright/test';

test.beforeEach(async({page})=>{
  await page.goto('./');
  await page.evaluate(()=>localStorage.removeItem('apurante_plus'));
  await page.reload();
});

test('cards save articles using only localStorage and keep an editorial snapshot',async({page,context})=>{
  const button=page.locator('.card [data-plus-save]').first();
  await expect(button).toBeVisible();
  const slug=await button.getAttribute('data-plus-save');
  await button.click();
  await expect(button).toHaveAttribute('aria-pressed','true');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.savedArticles).toContain(slug);
  expect(state.savedArticleSnapshots).toHaveLength(1);
  expect(state.savedArticleSnapshots[0].slug).toBe(slug);
  expect(state.savedArticleSnapshots[0].articleId).toMatch(/^apr-/);
  expect(state.savedArticleSnapshots[0].title).toBeTruthy();
  expect(state.savedArticleSnapshots[0].summary).toBeTruthy();
  expect(state.savedArticleSnapshots[0].lastModifiedAt).toBeTruthy();
  expect(await context.cookies()).toHaveLength(0);
});

test('Meu APURANTE controls Home visibility and order locally',async({page})=>{
  await page.goto('./meu-apurante/');
  await page.locator('[data-home-enabled]').check();
  const first=page.locator('[data-home-row]').first();
  const category=await first.getAttribute('data-category');
  await first.locator('[data-home-visible]').uncheck();
  await first.locator('[data-home-down]').click();
  await page.goto('./');
  await expect(page.locator('[data-plus-home-badge]')).toBeVisible();
  await expect(page.locator(`[data-home-category="${category}"]`)).toBeHidden();
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.preferences.home.enabled).toBe(true);
  expect(state.preferences.home.hiddenCategories).toContain(category);
});

test('APURANTE+ creates a single versioned .apurante backup and still imports legacy JSON',async({page})=>{
  await page.goto('./meu-apurante/');
  const downloadPromise=page.waitForEvent('download');
  await page.locator('[data-plus-export]').click();
  const download=await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^meu-apurante-\d{4}-\d{2}-\d{2}\.apurante$/);
  const legacy={app:'APURANTE+',schemaVersion:1,state:{version:1,interests:['Tecnologia'],savedArticles:[],followedTopics:['IA'],preferences:{compactFeed:false,home:{enabled:true,order:['Tecnologia'],hiddenCategories:[]}}}};
  await page.locator('[data-plus-import]').setInputFiles({name:'apurante-plus-config.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(legacy))});
  page.once('dialog',dialog=>dialog.accept());
  await page.locator('[data-plus-restore]').click();
  await expect(page.locator('[data-plus-portability-feedback]')).toContainText('restaurado com sucesso');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.version).toBe(3);
  expect(state.interests).toContain('Tecnologia');
  expect(state.followedTopics).toContain('IA');
  expect(state.preferences.home.enabled).toBe(true);
});

test('corrupted backup is rejected without touching current state',async({page})=>{
  await page.goto('./meu-apurante/');
  await page.evaluate(()=>localStorage.setItem('apurante_plus',JSON.stringify({version:3,interests:['Ciência'],savedArticles:[],savedArticleSnapshots:[],followedTopics:[],preferences:{compactFeed:false,home:{enabled:false,order:[],hiddenCategories:[],showPersonalFeed:true,showSavedShelf:true}}})));
  const before=await page.evaluate(()=>localStorage.getItem('apurante_plus'));
  await page.locator('[data-plus-import]').setInputFiles({name:'quebrado.apurante',mimeType:'application/octet-stream',buffer:Buffer.from('{não-é-json')});
  await expect(page.locator('[data-plus-portability-feedback]')).toContainText('corrompido ou adulterado');
  expect(await page.evaluate(()=>localStorage.getItem('apurante_plus'))).toBe(before);
  await expect(page.locator('[data-plus-restore]')).toBeDisabled();
});

test('unknown backup schema is rejected without guessing a migration',async({page})=>{
  await page.goto('./meu-apurante/');
  await page.evaluate(()=>localStorage.setItem('apurante_plus',JSON.stringify({version:3,interests:['Saúde'],savedArticles:[],savedArticleSnapshots:[],followedTopics:[],preferences:{compactFeed:false,home:{enabled:false,order:[],hiddenCategories:[],showPersonalFeed:true,showSavedShelf:true}}})));
  const before=await page.evaluate(()=>localStorage.getItem('apurante_plus'));
  const future={format:'apurante-backup',version:99,createdAt:new Date().toISOString(),encrypted:false,data:{state:{}}};
  await page.locator('[data-plus-import]').setInputFiles({name:'futuro.apurante',mimeType:'application/octet-stream',buffer:Buffer.from(JSON.stringify(future))});
  await page.locator('[data-plus-restore]').click();
  await expect(page.locator('[data-plus-portability-feedback]')).toContainText('versão ainda não suportada');
  expect(await page.evaluate(()=>localStorage.getItem('apurante_plus'))).toBe(before);
});

test('missing article IDs remain recoverable as local snapshots after restore',async({page})=>{
  await page.goto('./meu-apurante/');
  const backup={format:'apurante-backup',version:1,createdAt:new Date().toISOString(),encrypted:false,data:{state:{version:3,interests:[],savedArticles:['materia-que-saiu-do-ar'],savedArticleSnapshots:[{articleId:'apr-2025-01-01-abc1234',slug:'materia-que-saiu-do-ar',canonicalPath:'noticias/materia-que-saiu-do-ar/',title:'Matéria antiga preservada',summary:'Resumo preservado no momento do salvamento.',category:'Mundo',publishedAt:'2025-01-01T10:00:00Z',lastModifiedAt:'2025-01-01T10:00:00Z',savedAt:'2025-01-02T10:00:00Z'}],followedTopics:[],preferences:{compactFeed:false,home:{enabled:false,order:[],hiddenCategories:[],showPersonalFeed:true,showSavedShelf:true}}},appearance:{theme:'dark'},weatherLocation:null}};
  await page.locator('[data-plus-import]').setInputFiles({name:'arquivo.apurante',mimeType:'application/octet-stream',buffer:Buffer.from(JSON.stringify(backup))});
  page.once('dialog',dialog=>dialog.accept());
  await page.locator('[data-plus-restore]').click();
  await expect(page.locator('[data-plus-portability-feedback]')).toContainText('1 item(ns) antigo(s)');
  await expect(page.locator('.saved-archive-card')).toContainText('Matéria antiga preservada');
  await expect(page.locator('.saved-archive-card')).toContainText('não está mais disponível');
  const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_plus')));
  expect(state.savedArticles).toContain('materia-que-saiu-do-ar');
  expect(state.savedArticleSnapshots[0].summary).toContain('Resumo preservado');
});
