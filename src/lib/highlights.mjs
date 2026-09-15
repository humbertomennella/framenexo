// Urgency is an editorial decision with evidence and an expiry, never a keyword score.
const HOUR = 3_600_000;
const priorities = { normal: 0, watch: 1, important: 2, urgent: 3 };
const strongConfidence = confidence => ['CONFIRMADO', 'ALTA CONFIANÇA', 'ALTA_CONFIANCA'].includes(confidence);
const sourceIdentity = source => source?.originalOrganization || source?.organization || (()=>{try{return new URL(source.url).hostname}catch{return ''}})();
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
  const urls = new Set(review?.evidenceURLs || []);
  const supported = urls.size >= 2 && [...urls].every(url => article.sources.some(source => source.url === url)) && new Set(article.sources.filter(source => urls.has(source.url)).map(sourceIdentity).filter(Boolean)).size >= 2;
  const independent = hasIndependentEvidence(article);
  const strong = strongConfidence(article.confidence);
  const valid = review && review.level in priorities && reviewed >= published && reviewed <= now && expires > now && expires <= reviewed + (review.level === 'urgent' ? 3 : 12) * HOUR && supported && independent && strong && review.reason?.trim().length >= 20;
  if (!valid || review.level !== 'urgent') return null;
  const level = review.level;
  return { ...article, highlightLevel: level, highlightLabel: 'URGENTE', highlightExpiresAt: new Date(Math.min(published + 24 * HOUR, expires)).toISOString() };
}

export function selectHighlights(articles, now = Date.now()) {
 return articles.map(article => highlightFor(article, now)).filter(Boolean)
  .sort((a,b) => b.relevance-a.relevance || Date.parse(b.publishedAt)-Date.parse(a.publishedAt)).slice(0,3);
}
