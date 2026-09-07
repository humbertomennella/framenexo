# Validação da entrega — 7 de setembro de 2026

Este registro separa verificações realmente executadas de etapas que dependem do GitHub ainda não ativado.

## Executado com sucesso

- `npm ci` com Node.js 24 e lockfile presente.
- `npm test`: 28 testes Python passaram. Cobertura inclui janela real de dez horas, primeira publicação, pausa, idempotência/atomicidade, URLs e SSRF, redirecionamento, HTML não confiável, prompt injection, XXE, RSS/Atom, deduplicação de eventos, rumores, conteúdo fraco, modelo remoto, números não sustentados, HTML na saída e detecção de cópia.
- `astro build`: 27 páginas estáticas geradas.
- `npm run check:site`: passou com homepage, artigos, categorias, arquivo, 404, links internos, imagens, alt/dimensões, canonical, descriptions, JSON-LD, RSS, sitemap, robots e índice de busca.
- Busca visual: `exodus` retornou uma matéria, abriu a página correspondente e exibiu a origem. Busca sem resultados retornou estado vazio sem inserir HTML não confiável.
- Verificação móvel: iframe de 390 px apresentou conteúdo com `clientWidth=375` e `scrollWidth=375`, sem rolagem horizontal. A inspeção visual mostrou header compacto, navegação horizontal intencional, destaque empilhado e radar legível.
- Coleta real: 170 candidatos novos, 7 feeds respondendo e 1 timeout da IGN registrado no log. O texto bruto não foi publicado.
- Primeira edição: 6 matérias com URLs das fontes oficiais, sem imagens de jogos de terceiros. Títulos e resumos foram escritos para a edição, e o portal identifica o uso de IA.
- Execução anterior do modelo local: uma redação em português foi aprovada pela validação de formato e pela segunda passagem do modelo. Essa evidência é histórica; depois dela o extrator de fatos e os bloqueios contra inferência promocional foram endurecidos.

## Ainda não confirmado

- A nova combinação de extração de quatro fatos + redação curta + bloqueio de linguagem promocional não teve uma segunda execução completa após o endurecimento: o ambiente atingiu o limite de uso durante a tentativa. `data/deployment-status.json` permanece com `generationValidated: false`.
- GitHub Actions, GitHub Pages e a rotina horária não foram executados nesta sessão. O repositório dedicado `humbertomennella/framenexo` ainda não existia na consulta à conta.
- URL de Pages não foi apresentada como ativa. O endereço esperado, ainda não verificado, é `https://humbertomennella.github.io/framenexo/`.
- Não houve teste de Lighthouse/Core Web Vitals em produção, leitores RSS externos, indexação do Google News/Discover ou compatibilidade com todos os navegadores.

## Critério de conclusão operacional

Considerar o portal contínuo somente após: criar o repositório público dedicado; enviar o commit; ativar Pages; observar uma execução de `tests.yml`; observar uma execução do coletor com build/deploy; abrir a URL real retornada pelo GitHub; e substituir os campos pendentes em `data/deployment-status.json` por fatos observados.
