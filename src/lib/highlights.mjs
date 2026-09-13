// Urgency is an editorial decision with evidence and an expiry, never a keyword score.
const HOUR = 3_600_000;
const priorities = { normal: 0, watch: 1, important: 2, urgent: 3 };
const strongConfidence = confidence => ['CONFIRMADO', 'ALTA CONFIANÇA', 'ALTA_CONFIANCA'].includes(confidence);
const sourceIdentity = source => source?.originalOrganization || source?.organization || source?.url || '';
const hasIndependentEvidence = article => new Set((article.sources || []).map(sourceIdentity).filter(Boolean)).size >= 2;
const isPublishedVerified = (article, now) => {
  const published = Date.parse(article.publishedAt);
  return Number.isFinite(published) && published <= now && article.status === 'published' && strongConfidence(article.confidence) && hasIndependentEvidence(article);
};

export function highlightFor(article, now = Date.now()) {
  const published = Date.parse(article.publishedAt);
  if (!Number.isFinite(published) || published > now || now - published >= 24 * HOUR || article.status !== 'published' || ['RUMOR','RELATO'].includes(article.confidence)) return null;
  const review = article.highlight;
  const reviewed = Date.parse(review?.reviewedAt);
  const expires = Date.parse(review?.expiresAt);
  const supported = review?.evidenceURLs?.length >= 2 && review.evidenceURLs.every(url => article.sources.some(source => source.url === url));
  const independent = hasIndependentEvidence(article);
  const strong = strongConfidence(article.confidence);
  const valid = review && review.level in priorities && reviewed >= published && reviewed <= now && expires > now && expires <= reviewed + (review.level === 'urgent' ? 3 : 12) * HOUR && supported && independent && strong && review.reason?.trim().length >= 20;
  if (!valid || review.level !== 'urgent') return null;
  const level = review.level;
  return { ...article, highlightLevel: level, highlightLabel: 'URGENTE', highlightExpiresAt: new Date(Math.min(published + 24 * HOUR, expires)).toISOString() };
}

function watchFor(article, now = Date.now()) {
  if (!isPublishedVerified(article, now)) return null;
  return { ...article, highlightLevel: 'watch', highlightLabel: 'ACOMPANHAMENTO', highlightExpiresAt: null };
}

export function selectHighlights(articles, now = Date.now()) {
  const urgent = articles.map(article => highlightFor(article, now)).filter(Boolean)
    .sort((a, b) => priorities[b.highlightLevel] - priorities[a.highlightLevel] || b.relevance - a.relevance || b.publishedAt.localeCompare(a.publishedAt));
  if (urgent.length >= 3) return urgent.slice(0, 3);

  const used = new Set(urgent.map(article => article.slug));
  const verified = articles.map(article => watchFor(article, now)).filter(Boolean).filter(article => !used.has(article.slug));
  const recent = verified.filter(article => now - Date.parse(article.publishedAt) < 24 * HOUR)
    .sort((a, b) => (b.relevance || 0) - (a.relevance || 0) || b.publishedAt.localeCompare(a.publishedAt));
  const older = verified.filter(article => now - Date.parse(article.publishedAt) >= 24 * HOUR)
    .sort((a, b) => b.publishedAt.localeCompare(a.publishedAt) || (b.relevance || 0) - (a.relevance || 0));

  return [...urgent, ...recent, ...older].slice(0, 3);
}
