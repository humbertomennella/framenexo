export const WEATHER_STORAGE_KEY='apurante_weather_location';
export const WEATHER_CACHE_KEY='apurante_weather_cache';
export const WEATHER_CACHE_TTL=15*60*1000;

export function weatherPresentation(code=0,isDay=1,temperature=20){
  if([95,96,99].includes(code))return {kind:'storm',label:'Trovoadas'};
  if([71,73,75,77,85,86].includes(code))return {kind:'snow',label:'Neve'};
  if([56,57,66,67].includes(code))return {kind:'cold-rain',label:'Chuva congelante'};
  if([51,53,55].includes(code))return {kind:'drizzle',label:'Garoa'};
  if([61,63,65,80,81,82].includes(code))return {kind:'rain',label:'Chuva'};
  if([45,48].includes(code))return {kind:'fog',label:'Neblina'};
  if(code===3)return {kind:'cloudy',label:'Nublado'};
  if(code===1||code===2)return {kind:'partly-cloudy',label:'Parcialmente nublado'};
  if(temperature<=8)return {kind:'cold',label:'Frio'};
  return isDay?{kind:'clear-day',label:'Céu limpo'}:{kind:'clear-night',label:'Céu limpo'};
}

export function normalizeLocation(result){
  return {
    id:Number(result.id)||null,
    name:String(result.name||''),
    admin1:String(result.admin1||''),
    country:String(result.country||''),
    latitude:Number(result.latitude),
    longitude:Number(result.longitude),
    timezone:String(result.timezone||'auto')
  };
}
