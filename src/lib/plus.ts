export const PLUS_STORAGE_KEY = 'apurante_plus';
export const PLUS_SCHEMA_VERSION = 3;

export interface SavedArticleSnapshot {
  articleId: string;
  slug: string;
  canonicalPath: string;
  title: string;
  summary: string;
  category: string;
  publishedAt: string;
  lastModifiedAt: string;
  savedAt: string;
}

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
  version: 3;
  interests: string[];
  savedArticles: string[];
  savedArticleSnapshots: SavedArticleSnapshot[];
  followedTopics: string[];
  preferences: PlusPreferences;
}

export const defaultPlusState = (): PlusState => ({
  version: PLUS_SCHEMA_VERSION,
  interests: [],
  savedArticles: [],
  savedArticleSnapshots: [],
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

const cleanString = (value: unknown) => typeof value === 'string' ? value.trim() : '';
const cleanList = (value: unknown) => Array.isArray(value)
  ? [...new Set(value.filter(item => typeof item === 'string' && item.trim()).map(item => item.trim()))]
  : [];

const normalizeSnapshot = (value: unknown): SavedArticleSnapshot | null => {
  if (!value || typeof value !== 'object') return null;
  const item = value as Partial<SavedArticleSnapshot>;
  const slug = cleanString(item.slug);
  const articleId = cleanString(item.articleId);
  if (!slug && !articleId) return null;
  return {
    articleId: articleId || `legacy:${slug}`,
    slug,
    canonicalPath: cleanString(item.canonicalPath) || (slug ? `noticias/${slug}/` : ''),
    title: cleanString(item.title) || slug.replace(/-/g, ' '),
    summary: cleanString(item.summary),
    category: cleanString(item.category),
    publishedAt: cleanString(item.publishedAt),
    lastModifiedAt: cleanString(item.lastModifiedAt),
    savedAt: cleanString(item.savedAt),
  };
};

const normalizeSnapshots = (value: unknown) => {
  if (!Array.isArray(value)) return [];
  const unique = new Map<string, SavedArticleSnapshot>();
  value.forEach(raw => {
    const snapshot = normalizeSnapshot(raw);
    if (!snapshot) return;
    unique.set(snapshot.articleId || snapshot.slug, snapshot);
  });
  return [...unique.values()];
};

export function normalizePlusState(value: unknown): PlusState {
  if (!value || typeof value !== 'object') return defaultPlusState();
  const candidate = value as Partial<PlusState>;
  const home = candidate.preferences?.home;
  const savedArticles = cleanList(candidate.savedArticles);
  const snapshots = normalizeSnapshots((candidate as any).savedArticleSnapshots)
    .filter(item => !item.slug || savedArticles.includes(item.slug));
  return {
    version: PLUS_SCHEMA_VERSION,
    interests: cleanList(candidate.interests),
    savedArticles,
    savedArticleSnapshots: snapshots,
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
    try {
      window.localStorage.setItem(PLUS_STORAGE_KEY, JSON.stringify(normalized));
      window.dispatchEvent(new CustomEvent('apurante-plus:change', {detail: normalized}));
    } catch (error) {
      window.dispatchEvent(new CustomEvent('apurante-plus:storage-error', {detail: error}));
    }
  }
  return normalized;
}

const toggle = (items: string[], value: string, force?: boolean) => {
  const exists = items.includes(value);
  const include = force ?? !exists;
  return include ? [...new Set([...items, value])] : items.filter(item => item !== value);
};

export function toggleSavedArticle(slug: string, force?: boolean, snapshot?: SavedArticleSnapshot) {
  const state = readPlusState();
  const exists = state.savedArticles.includes(slug);
  const include = force ?? !exists;
  state.savedArticles = toggle(state.savedArticles, slug, force);
  if (!include) {
    state.savedArticleSnapshots = state.savedArticleSnapshots.filter(item => item.slug !== slug);
  } else if (snapshot) {
    const normalized = normalizeSnapshot({...snapshot, slug});
    if (normalized) {
      const previous = state.savedArticleSnapshots.find(item => item.articleId === normalized.articleId || item.slug === slug);
      normalized.savedAt = previous?.savedAt || normalized.savedAt || new Date().toISOString();
      state.savedArticleSnapshots = state.savedArticleSnapshots.filter(item => item.articleId !== normalized.articleId && item.slug !== slug);
      state.savedArticleSnapshots.push(normalized);
    }
  }
  return writePlusState(state);
}

export function getSavedSnapshot(state: PlusState, articleId: string, slug: string) {
  return state.savedArticleSnapshots.find(item => (articleId && item.articleId === articleId) || item.slug === slug);
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
