export type CalendarThemePalette = {
  accent: string;
  accentText: string;
  linkHover: string;
  buttonText: string;
  surfaceTint: string;
};

export type CalendarTheme = {
  id: string;
  start: string;
  end: string;
  label: string;
  shortLabel: string;
  message: string;
  link?: string;
  linkLabel?: string;
  palette: {
    light: CalendarThemePalette;
    dark: CalendarThemePalette;
  };
};

export const calendarThemes: CalendarTheme[] = [
  {
    id: 'setembro-amarelo',
    start: '09-01',
    end: '09-30',
    label: 'Setembro Amarelo',
    shortLabel: 'Setembro Amarelo',
    message: 'Um mês de valorização da vida, escuta e cuidado.',
    link: 'https://cvv.org.br/',
    linkLabel: 'Informação e apoio',
    palette: {
      light: {
        accent: '#e1b900',
        accentText: '#6b5600',
        linkHover: '#4b3c00',
        buttonText: '#171200',
        surfaceTint: '#fff8d8'
      },
      dark: {
        accent: '#ffd84d',
        accentText: '#ffe170',
        linkHover: '#fff1a8',
        buttonText: '#181300',
        surfaceTint: '#211d0d'
      }
    }
  }
];

const mmdd = (date: Date, timeZone = 'America/Sao_Paulo') => {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    month: '2-digit',
    day: '2-digit'
  }).formatToParts(date);
  const month = parts.find(part => part.type === 'month')?.value || '01';
  const day = parts.find(part => part.type === 'day')?.value || '01';
  return `${month}-${day}`;
};

export const isDateInsideTheme = (key: string, start: string, end: string) =>
  start <= end ? key >= start && key <= end : key >= start || key <= end;

export const resolveCalendarTheme = (date = new Date(), timeZone = 'America/Sao_Paulo') => {
  const key = mmdd(date, timeZone);
  return calendarThemes.find(theme => isDateInsideTheme(key, theme.start, theme.end)) || null;
};
