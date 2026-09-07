# Segurança e limites

- **Rede:** somente HTTPS e hosts exatos do cadastro; portas não padrão, credenciais em URL, IPs privados e redirecionamentos externos são recusados. Na presença de proxy HTTPS, a resolução de destino cabe ao proxy; a verificação de domínio continua obrigatória.
- **Conteúdo externo:** limite de tamanho, timeouts, tentativas limitadas e RSS/Atom sem DTD/entidades. HTML de script, navegação e estilos é removido. Leitura alternativa de artigos depende de robots e de uma fronteira de artigo identificável.
- **Prompt injection:** fontes são dados, sem poder de alterar instruções. Heurísticas bloqueiam padrões conhecidos; não são defesa completa. O modelo não dispõe de ferramentas, shell, navegador ou credenciais e sua saída precisa passar pelos controles posteriores.
- **Publicação:** campos estruturados, frontmatter JSON, proibição de HTML e links gerados no corpo, fontes escolhidas pelo coletor e gravação exclusiva de novo arquivo. Markdown é renderizado estaticamente, sem MDX. JSON-LD escapa caracteres de abertura de tags. Busca usa `textContent`, sem injetar HTML.
- **Modelo:** motor e pesos fixados por revisão e SHA-256; extração de tar com filtro de segurança. Serviço somente em loopback, sem API paga. Downloads não são executados antes da verificação.
- **GitHub:** jobs separados por permissão, Actions fixadas por SHA, nenhuma credencial persistida no checkout. Apenas a etapa de push recebe token de escrita; coleta e modelo rodam antes dela. Avisos de falha só leem código confiável de main do mesmo repositório.
- **Dados:** estado JSON gravado atomicamente, trava de processo e concorrência do workflow; prevenção de commit vazio e push forçado. Logs públicos resumidos não carregam texto bruto, segredos ou prompts completos. Metadados de candidatos e auditoria ficam no repositório, que será público.
- **Recuperação:** arquivos publicados são lidos para reconstruir o conjunto de eventos já existentes. Falhas não autorizam excluir notícias válidas ou fazer rollback destrutivo. Conflitos de push permanecem visíveis e requerem resolução normal.

Riscos residuais: dependência da integridade das fontes, vulnerabilidades dos parsers/bibliotecas, erros factuais do modelo, classificações equivocadas e deduplicação incompleta entre idiomas. Uma segunda verificação pelo mesmo modelo pode repetir o mesmo erro. Retidos devem ser revisados, e a operação precisa de acompanhamento editorial.

Nenhuma chave, senha ou token deve ser adicionada ao código. Atualizações de acesso global, domínio, custo ou infraestrutura exigem decisão do responsável. Dependabot propõe mudanças; não faz merge automaticamente.
