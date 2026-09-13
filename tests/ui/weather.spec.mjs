import {test,expect} from '@playwright/test';

const geocoding={results:[{id:3464975,name:'Curitiba',latitude:-25.4278,longitude:-49.2731,elevation:934,feature_code:'PPLA',country_code:'BR',admin1_id:6322752,admin2_id:6322731,timezone:'America/Sao_Paulo',population:1948626,country_id:3469034,country:'Brasil',admin1:'Paraná',admin2:'Curitiba'}]};
const weather={latitude:-25.4,longitude:-49.3,generationtime_ms:.1,utc_offset_seconds:-10800,timezone:'America/Sao_Paulo',timezone_abbreviation:'BRT',elevation:924,current_units:{time:'iso8601',interval:'seconds',temperature_2m:'°C',apparent_temperature:'°C',weather_code:'wmo code',is_day:'',precipitation:'mm',rain:'mm',snowfall:'cm',wind_speed_10m:'km/h'},current:{time:'2026-09-13T02:00',interval:900,temperature_2m:12.6,apparent_temperature:10.2,weather_code:61,is_day:0,precipitation:.6,rain:.6,snowfall:0,wind_speed_10m:14.2}};

test.beforeEach(async({page})=>{
  await page.route('https://geocoding-api.open-meteo.com/**',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(geocoding)}));
  await page.route('https://api.open-meteo.com/**',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(weather)}));
  await page.goto('./');
  await page.evaluate(()=>{localStorage.removeItem('apurante_weather_location');localStorage.removeItem('apurante_weather_cache');});
  await page.reload();
});

test('reader selects a city and sees current weather with matching icon',async({page})=>{
  const summary=page.locator('[data-weather-toggle]');
  await expect(summary).toContainText('Escolha sua cidade');
  await summary.click();
  await page.getByPlaceholder('Digite sua cidade').fill('Curitiba');
  await page.locator('[data-weather-search] button[type="submit"]').click();
  await page.getByRole('option').filter({hasText:'Curitiba'}).click();
  await expect(summary).toContainText('Curitiba');
  await expect(summary).toContainText('13°');
  await expect(summary).toContainText('Chuva');
  await expect(page.locator('[data-weather-icon] svg')).toBeVisible();
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('apurante_weather_location')));
  expect(saved.name).toBe('Curitiba');
});

test('saved weather location survives reload without asking again',async({page})=>{
  await page.evaluate(()=>localStorage.setItem('apurante_weather_location',JSON.stringify({id:3464975,name:'Curitiba',admin1:'Paraná',country:'Brasil',latitude:-25.4278,longitude:-49.2731,timezone:'America/Sao_Paulo'})));
  await page.reload();
  const summary=page.locator('[data-weather-toggle]');
  await expect(summary).toContainText('Curitiba');
  await expect(summary).toContainText('13°');
  await expect(summary).toContainText('Chuva');
});

test('weather bar stays compact on a 360px viewport',async({page})=>{
  await page.setViewportSize({width:360,height:800});
  await page.reload();
  await expect(page.locator('[data-weather]')).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  expect(await page.locator('[data-weather]').evaluate(el=>Math.round(el.getBoundingClientRect().height))).toBeLessThan(45);
});
