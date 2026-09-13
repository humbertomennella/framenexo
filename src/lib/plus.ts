export const PLUS_STORAGE_KEY = 'apurante_plus';
export const PLUS_SCHEMA_VERSION = 2;

export interface HomePreferences {
  enabled: boolean;
  order: string[];
  hiddenCategories: string[];
  showPersonalFeed: boolean;
  showSavedShelf: boolean;
}

export interface PlusPreferences {
  compactFeed: boolean;
  home: HomePreferences;
}

export interface PlusState {
  version: 2;
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
  preferences: {
    compactFeed: false,
    home: {
      enabled: false,
      order: [],
      hiddenCategories: [],
      showPersonalFeed: true,
      showSavedShelf: true,
    },
  },
});

const cleanList = (value: unknown) => Array.isArray(value)
  ? [...new Set(value.filter(item => typeof item === 'string' && item.trim()).map(item => item.trim()))]
  : [];

export function normalizePlusState(value: unknown): PlusState {
  if (!value || typeof value !== 'object') return defaultPlusState();
  const candidate = value as Partial<PlusState>;
  const home = candidate.preferences?.home;
  return {
    version: PLUS_SCHEMA_VERSION,
    interests: cleanList(candidate.interests),
    savedArticles: cleanList(candidate.savedArticles),
    followedTopics: cleanList(candidate.followedTopics),
    preferences: {
      compactFeed: Boolean(candidate.preferences?.compactFeed),
      home: {
        enabled: Boolean(home?.enabled),
        order: cleanList(home?.order),
        hiddenCategories: cleanList(home?.hiddenCategories),
        showPersonalFeed: home?.showPersonalFeed !== false,
        showSavedShelf: home?.showSavedShelf !== false,
      },
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

export function setCompactFeed(compactFeed: boolean) {
  const state = readPlusState();
  state.preferences.compactFeed = Boolean(compactFeed);
  return writePlusState(state);
}

export function setHomePreferences(home: HomePreferences) {
  const state = readPlusState();
  state.preferences.home = {
    enabled: Boolean(home.enabled),
    order: cleanList(home.order),
    hiddenCategories: cleanList(home.hiddenCategories),
    showPersonalFeed: home.showPersonalFeed !== false,
    showSavedShelf: home.showSavedShelf !== false,
  };
  return writePlusState(state);
}

export function hasPersonalization(state = readPlusState()) {
  return Boolean(
    state.interests.length ||
    state.savedArticles.length ||
    state.followedTopics.length ||
    state.preferences.compactFeed ||
    state.preferences.home.enabled
  );
}

export function clearPlusState() {
  return writePlusState(defaultPlusState());
}
