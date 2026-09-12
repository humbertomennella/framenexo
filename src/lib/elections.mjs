const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export function selectElections(articles, now = Date.now()) {
  return articles.filter(a => a.status === 'published' && Date.parse(a.publishedAt) <= now &&
    !['RUMOR', 'RELATO'].includes(a.confidence) &&
    new Set((a.sources || []).map(source => source.originalOrganization || source.organization || new URL(source.url).hostname)).size >= 2 &&
    (a.electionCoverage === true || (a.electionCoverage == null && (a.tags || []).some(tag => /^eleicoes(?: 2026)?$/.test(normalize(tag))))))
    .sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
}
