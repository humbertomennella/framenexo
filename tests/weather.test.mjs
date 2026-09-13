import test from 'node:test';
import assert from 'node:assert/strict';
import {weatherPresentation,normalizeLocation} from '../src/lib/weather.mjs';

test('weather codes map to stable APURANTE conditions',()=>{
  assert.deepEqual(weatherPresentation(0,1,24),{kind:'clear-day',label:'Céu limpo'});
  assert.deepEqual(weatherPresentation(0,0,18),{kind:'clear-night',label:'Céu limpo'});
  assert.deepEqual(weatherPresentation(2,1,20),{kind:'partly-cloudy',label:'Parcialmente nublado'});
  assert.deepEqual(weatherPresentation(61,1,16),{kind:'rain',label:'Chuva'});
  assert.deepEqual(weatherPresentation(75,1,-1),{kind:'snow',label:'Neve'});
  assert.deepEqual(weatherPresentation(95,1,22),{kind:'storm',label:'Trovoadas'});
  assert.deepEqual(weatherPresentation(0,1,6),{kind:'cold',label:'Frio'});
});

test('geocoding results are normalized before persistence',()=>{
  assert.deepEqual(normalizeLocation({id:1,name:'Curitiba',admin1:'Paraná',country:'Brasil',latitude:-25.43,longitude:-49.27,timezone:'America/Sao_Paulo'}),{
    id:1,name:'Curitiba',admin1:'Paraná',country:'Brasil',latitude:-25.43,longitude:-49.27,timezone:'America/Sao_Paulo'
  });
});
