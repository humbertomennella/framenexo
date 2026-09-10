// Urgency is an editorial decision with evidence and an expiry, never a keyword score.
const HOUR = 3_600_000;
const priorities = { normal: 0, important: 1, urgent: 2 };
export function highlightFor(article, now = Date.now()) {
  const published = Date.parse(article.publishedAt);
  if (!Number.isFinite(published) || published > now || now - published >= 24 * HOUR || article.status !== 'published' || ['RUMOR','RELATO'].includes(article.confidence)) return null;
  const review = article.highlight;
  const reviewed = Date.parse(review?.reviewedAt);
  const expires = Date.parse(review?.expiresAt);
  const supported = review?.evidenceURLs?.length >= 2 && review.evidenceURLs.every(url => article.sources.some(source => source.url === url));
  const independent = new Set(article.sources.map(source => source.originalOrganization || source.organization || new URL(source.url).hostname)).size >= 2;
  const strong = ['CONFIRMADO', 'ALTA CONFIANÇA', 'ALTA_CONFIANCA'].includes(article.confidence);
  const valid = review && review.level in priorities && reviewed >= published && reviewed <= now && expires > now && expires <= reviewed + (review.level === 'urgent' ? 3 : 12) * HOUR && supported && independent && strong && review.reason?.trim().length >= 20;
  if (!valid || review.level !== 'urgent') return null;
  const level = review.level;
  return { ...article, highlightLevel: level, highlightLabel: 'URGENTE', highlightExpiresAt: new Date(Math.min(published + 24 * HOUR, expires)).toISOString() };
}
export function selectHighlights(articles, now = Date.now()) {
  return articles.map(article => highlightFor(article, now)).filter(Boolean)
    .sort((a, b) => priorities[b.highlightLevel] - priorities[a.highlightLevel] || b.relevance - a.relevance || b.publishedAt.localeCompare(a.publishedAt)).slice(0, 3);
}
