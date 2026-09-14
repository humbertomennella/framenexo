# Validação operacional — 14 de setembro de 2026

Este documento registra o estado observado do APURANTE depois da recuperação do pipeline editorial e substitui o relatório inicial de 7 de setembro, que já não representava a produção.

## Produção confirmada

- Repositório público: `humbertomennella/framenexo`.
- Site público: `https://humbertomennella.github.io/framenexo/`.
- Frontend estático em Astro publicado pelo GitHub Pages.
- Grade editorial pública: **08h, 13h, 18h e 22h**, horário de Brasília (`America/Sao_Paulo`).
- Cron regular do GitHub Actions: `0 1,11,16,21 * * *` em UTC.
- Edições extraordinárias podem ser acionadas fora da grade sem consumir o próximo slot regular.
- O deploy #73, associado à edição extraordinária de 14/09, terminou com sucesso.

## Scout

- O Scout roda a cada 15 minutos.
- Ele possui somente leitura do repositório e não pode publicar, fazer commit ou executar deploy.
- O pool transitório é transportado em GitHub Actions Artifact e validado por versão, repositório, run, idade e SHA-256.
- A execução real observada em 14/09 alcançou 15 fontes, adicionou 13 candidatos e preservou centenas de candidatos acumulados no snapshot.
- Falhas individuais de fonte são registradas como degradação parcial; não zeram o pool e não liberam publicação sem evidência.

## Fechamento editorial

O fechamento regular só pode publicar depois de:

1. recuperar um snapshot de Scout concluído e válido;
2. agrupar candidatos e exigir rotas independentes para matéria completa;
3. obter evidência textual verificável;
4. gerar e revisar o texto;
5. obter mídia autorizada ou usar a solução editorial original prevista pelo projeto;
6. executar testes, build e verificação do site;
7. persistir somente uma edição efetivamente aprovada.

Uma falha no passo editorial não pode seguir para validação, commit ou deploy. Dados transitórios do Scout, logs de coleta e alterações de status sem nova matéria não constituem uma edição e não devem gerar commit no `main`.

## Cobertura automatizada

A suíte Python cobre, entre outros pontos:

- horário de Brasília e os quatro slots regulares;
- limite e balanceamento por editoria;
- confirmação entre organizações independentes;
- republicações de agência;
- conflito factual;
- rumores e opinião;
- aquisição e licença de mídia;
- duplicação de mídia;
- idempotência de publicação;
- URLs, SSRF e redirecionamentos;
- XML/XXE e conteúdo HTML não confiável;
- snapshots do Scout, checksum, origem, idade e fallback;
- isolamento do Scout em relação a commit e deploy;
- falhas parciais de fontes;
- consistência entre estado editorial e artigos publicados.

O frontend também passa por testes JavaScript, `astro build`, `npm run check:site` e Playwright/Chromium. `check:site` verifica rotas, H1, canonical, descrição, imagens, links, JSON-LD, sitemap, robots, busca, regras editoriais, fontes e extensão mínima de matérias.

## Contrato de recuperação

A auditoria de 14/09 adiciona regressões explícitas para impedir que:

- um pipeline editorial com falha chegue ao commit;
- o Scout volte a versionar `candidates.json` ou `scout-state.json` no `main`;
- alterações apenas transitórias criem uma falsa edição;
- o estado durável fique atrás do artigo público mais recente;
- domínio legado volte a ser usado como canonical de fallback;
- a abreviação antiga `A+` reapareça no artigo;
- a grade pública de 08h, 13h, 18h e 22h seja alterada acidentalmente.

## Limites conhecidos

O GitHub Actions pode atrasar cron jobs; o horário define a edição editorial, não uma garantia de início no segundo exato. Fontes externas podem sofrer indisponibilidade, alterar feeds ou impor bloqueios. Esses casos devem degradar a coleta de forma visível sem derrubar a versão já publicada do site.

Lighthouse/Core Web Vitals, indexação de mecanismos externos e disponibilidade de terceiros não são garantias do pipeline editorial. Eles devem ser monitorados separadamente e não podem ser usados para contornar paywall, CAPTCHA, autenticação ou termos dos provedores.

## Critério de liberação

Uma alteração de recuperação só deve chegar ao `main` quando a CI completa da própria alteração passar. Depois do merge, o deploy do Pages deve terminar com sucesso e a Home, a matéria mais recente, o Arquivo e o cronograma público devem ser conferidos na versão publicada.
