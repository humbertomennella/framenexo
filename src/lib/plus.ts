export const PLUS_STORAGE_KEY = 'apurante_plus';
export const PLUS_SCHEMA_VERSION = 1;

export interface PlusPreferences {
  compactFeed: boolean;
}

export interface PlusState {
  version: 1;
  interests: string[];
  savedArticles: string[];
  followedTopics: string[];
  preferences: PlusPreferences;
}

export const defaultPlusState = (): PlusState => ({
  version: PLUS_SCHEMA_VERSION,
  interests: [],
  savedArticles: [],
  followedTopics: [],
  preferences: {compactFeed: false},
});

const cleanList = (value: unknown) => Array.isArray(value)
  ? [...new Set(value.filter(item => typeof item === 'string' && item.trim()).map(item => item.trim()))]
  : [];

export function normalizePlusState(value: unknown): PlusState {
  if (!value || typeof value !== 'object') return defaultPlusState();
  const candidate = value as Partial<PlusState>;
  return {
    version: PLUS_SCHEMA_VERSION,
    interests: cleanList(candidate.interests),
    savedArticles: cleanList(candidate.savedArticles),
    followedTopics: cleanList(candidate.followedTopics),
    preferences: {
      compactFeed: Boolean(candidate.preferences?.compactFeed),
    },
  };
}

export function readPlusState(): PlusState {
  if (typeof window === 'undefined') return defaultPlusState();
  try {
    return normalizePlusState(JSON.parse(window.localStorage.getItem(PLUS_STORAGE_KEY) || 'null'));
  } catch {
    return defaultPlusState();
  }
}

export function writePlusState(state: PlusState): PlusState {
  const normalized = normalizePlusState(state);
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(PLUS_STORAGE_KEY, JSON.stringify(normalized));
    window.dispatchEvent(new CustomEvent('apurante-plus:change', {detail: normalized}));
  }
  return normalized;
}

const toggle = (items: string[], value: string, force?: boolean) => {
  const exists = items.includes(value);
  const include = force ?? !exists;
  return include ? [...new Set([...items, value])] : items.filter(item => item !== value);
};

export function toggleSavedArticle(slug: string, force?: boolean) {
  const state = readPlusState();
  state.savedArticles = toggle(state.savedArticles, slug, force);
  return writePlusState(state);
}

export function toggleFollowedTopic(topic: string, force?: boolean) {
  const state = readPlusState();
  state.followedTopics = toggle(state.followedTopics, topic, force);
  return writePlusState(state);
}

export function setInterests(interests: string[]) {
  const state = readPlusState();
  state.interests = cleanList(interests);
  return writePlusState(state);
}

export function clearPlusState() {
  return writePlusState(defaultPlusState());
}
