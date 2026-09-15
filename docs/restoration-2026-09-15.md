# Restauração segura — 15/09/2026

Base: main 0186693b4c93aacb00251d868ad46e5853eae64d.

## Contratos restaurados

- Novas matérias completas exigem duas organizações independentes e revisão do mesmo núcleo factual. Fonte primária isolada não basta. Política v4.
- Legado de rota única permanece acessível com selo Relato, nota de revisão e URLs estáveis; esta manutenção não comprova novamente os fatos históricos.
- URGENTE não usa notícias comuns ou antigas para ocupar posições. Expiração local funciona mesmo com um único slide e movimento reduzido.
- Eleições e urgências consultam a edição publicada a cada 60 segundos enquanto visíveis, sem simular notícia nova. Publicação depende de fechamento e evidência.
- Cron principal 0 1,11,16,21 UTC = 22h do dia anterior, 08h, 13h, 18h em Brasília. Recuperação :27. GitHub pode atrasar o início; geração e verificação levam tempo.
- Scout continua em artifacts, sem commits; relatórios de cada fechamento também são artifacts, inclusive retenções/falhas, com identificação real da execução.

## Correções

Leitura integral pública priorizada, suporte ao corpo Agência Brasil, rejeição de conteúdo pago explicitamente marcado, resumos muito curtos impedidos de substituir uma matéria integral, expansão gzip limitada durante leitura, evidências compartilhadas incluídas no registro permanente, equilíbrio cronológico das últimas vinte matérias, revalidação completa após rebase.

Canais da Câmara consolidados no feed geral; outros canais permanecem cadastrados e desativados. Não foram inventados novos feeds.

Capa tipográfica de contingência passa a ser SVG exclusivo, escapado, sem referências externas ou script, com origem, escopo e hash. Não altera fotografias/ilustrações existentes. Não é imagem de fotojornalismo nem reconstrução do acontecimento. Créditos de terceiros não são truncados. Falta de imagem licenciada não produz fotografia fictícia.

## Limites

Os testes de pipeline usam modelos controlados e não certificam uma futura notícia. Modelo que escreve e revisa continua sendo o mesmo, sem independência humana. Nenhuma afirmação de horário exato, vinte matérias por edição, Lighthouse máximo ou eliminação de todos os erros futuros. O acervo com apenas uma rota exige apuração adicional antes de receber confiança superior.
