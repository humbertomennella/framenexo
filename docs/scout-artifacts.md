# Scout: snapshots transitórios em Actions Artifacts

## Escopo e auditoria da fase 1

Base auditada: `main`, commit `017eb23c4eab05e5c85d2165ee10a765c3a233e0`.

| Arquivo / estado | Antes | Nesta fase |
| --- | --- | --- |
| `.github/workflows/scout.yml` | A cada 15 minutos; permissão de escrita; mesmo bloqueio do fechamento; commit de quatro arquivos de estado. | Mesmo cron UTC; somente leitura de conteúdo e Actions; bloqueio próprio; artifact imutável; nenhuma publicação ou commit. |
| `.github/workflows/collector.yml` | Coletava novamente durante o fechamento. | Restaura um snapshot válido de execução concluída antes de iniciar o pipeline existente. Mantém validação e publicação existentes. |
| `.github/workflows/publisher.yml` | Reutiliza o collector. | Continua reutilizando; explicita permissões de leitura de artifacts e de issues requeridas pelo workflow chamado. |
| `scripts/run_scout.py` | `collect()` gravava diretamente em `data/`, incluindo relógio de coleta e log. | Reutiliza `collect()` com roteamento temporário para `.cache/scout/`; valida e emite snapshot. |
| `scripts/commit_scout.py` | `git add`, commit e push para `main`. | Entrada aposentada: termina com erro explicativo, sem executar Git. |
| `scripts/run_editorial.py` | `collect()` antes da verificação e inicialização do modelo. | Consome snapshot validado; ausência/corrupção retém edição antes do modelo. |
| `scripts/publish_edition.py` | Verifica fontes, mídia, duplicidade; gera ID e slug; cria matéria com abertura exclusiva. | Sem alteração. Teste de integração confirma publicação e reexecução idempotente a partir de snapshot. |
| `scripts/pipeline.py` | Leitura/escrita de JSON centralizada; coleta com limites, deduplicação e retries por fonte. | Adiciona contexto de roteamento de estado. Coleta, evidência e régua editorial permanecem as mesmas. |
| `data/candidates.json` | Pool operacional e decisões editoriais misturados. | Mantido como registro do último fechamento e semente de recuperação; Scout não o modifica. Decisões anteriores e mídia aprovada são reconciliadas por URL. |
| `data/scout-state.json` | Atualizado por commit a cada Scout. | Atualizado somente ao consumir snapshot no fechamento, com timestamp real do Scout, sem simular atualização contínua. |
| `data/publishing-state.json` | Relógio da coleta e histórico durável de publicação. | Scout usa cópia temporária; fechamento continua dono do relógio editorial e histórico durável. |
| `data/editorial-log.json` | Recebia eventos de cada Scout. | Eventos do Scout ficam temporários e no resumo do Actions; decisões do fechamento continuam duráveis. |
| `data/operation-state.json`, `data/deployment-status.json` | Resultado do fechamento e dados da implantação. | Fluxo preservado; resultado inclui identificação e horário do snapshot consumido. |
| `data/sources.json`, `data/image-rights.json`, `data/evidence/`, `data/edition-schedule.json` | Fontes, direitos, evidências e calendário. | Sem alteração de políticas ou conteúdo. |

O notificador antigo do Scout lia `operation-state.json`, referente ao fechamento anterior. A chamada foi retirada do Scout; seu resultado verdadeiro agora aparece no resumo da própria execução. Falhas totais deixam o workflow vermelho. O notificador do fechamento permanece intacto.

## Contrato do snapshot

- Artifact: `apurante-scout-v1-<run_id>-<run_attempt>`; retenção de 7 dias, compressão nível 9.
- Conteúdo único: `snapshot.json`, com envelope versionado e SHA-256 do payload canônico.
- Payload: repositório, execução/tentativa, horário real de conclusão da coleta, candidatos e resultado das fontes; `publishingAllowed: false`.
- Download limitado a 12 MB; ZIP não é extraído para o filesystem. Layout, checksum, versão, campos, origem, execução, idade e sucesso parcial são validados.
- Somente execução de `scout.yml` concluída com sucesso, em `main`, originada por schedule/push/workflow_dispatch. Artifacts de execuções em andamento ou falhas são ignorados. O token não acompanha redirects para o armazenamento do artifact.
- Snapshot utilizável por até 24 horas. Candidatos expiram após 7 dias; entradas expiradas/publicadas são removidas, URLs são normalizadas e deduplicadas, limite de 2.000 candidatos preservado.
- Checksum detecta corrupção, não prova veracidade jornalística. A confiança no transporte também depende da origem do workflow; verificação factual continua no publicador.

## Recuperação e concorrência

| Situação | Comportamento |
| --- | --- |
| Instalação inicial / nenhum artifact utilizável, sem erro da API | Scout usa candidatos ainda válidos do último fechamento como semente e realiza nova coleta. Só emite snapshot após alcançar pelo menos uma fonte. |
| Artifact recente corrompido ou expirado | Busca anterior válido; nunca consome execução falha. Se houve erro e nenhum fallback é válido, Scout falha conservadoramente, sem substituir o pool por um snapshot incompleto. |
| API indisponível / limite de requisições | Não reinicia o pool às cegas. Próxima execução tenta novamente; fechamento sem snapshot retém a edição. |
| Falha parcial de fontes | Preserva candidatos anteriores ainda válidos; incorpora respostas disponíveis; snapshot `degraded` registra as fontes com erro. Os retries existentes de coleta são preservados. |
| Todas as fontes falham | Nenhum novo snapshot é publicado; o último concluído e válido permanece disponível. |
| Execução atrasada / reexecução | Seleção por conclusão registrada no Actions, com validação de idade e tentativa. Atraso não altera horários de publicação nem cria fatos novos. |
| Dois Scouts | Grupo `apurante-scout-snapshot`, sem cancelamento da execução ativa; lock local adicional. Jobs pendentes podem ser substituídos pelo GitHub: cron não é garantia de execução pontual. |
| Scout e fechamento simultâneos | Grupos distintos; fechamento lê apenas artifact imutável de execução concluída. Artigo publicado é a autoridade para deduplicação, mesmo se o snapshot anteceder a publicação. |
| Scout falha após coletar | Artifact de run falho não é elegível. Scout não possui escrita em conteúdo nem etapa de deploy; o site publicado permanece intacto. |

A restauração examina até quatro páginas de 100 execuções bem-sucedidas. Isso cobre mais de um dia no ritmo normal. Execuções manuais excessivas ou indisponibilidade prolongada podem causar retenção conservadora. Não há branch de telemetria, cache mutável usado como banco, serviço pago novo ou segredo adicional.

## Horários e custos

Scout: `*/15 * * * *` UTC, inalterado. Fechamento: `0 1,11,16,21 * * *` UTC, correspondente a 22h/08h/13h/18h em Brasília. Modelo local e trabalho editorial pesado permanecem nos fechamentos; execução manual extraordinária já existente é preservada.

Actions Artifacts oferece snapshots imutáveis entre runs sem commits. Retenção curta, compressão e limites reduzem armazenamento; consumo real continua sujeito à franquia e disponibilidade do GitHub. Não se promete custo zero ilimitado ou disponibilidade de 100%.

## Validação e operação

Executar `python3 -m unittest discover -s tests -v`, `npm test`, `npm run build`, `npm run check:site`, `npm run test:ui`. Os testes de snapshots simulam o transporte e o modelo; não fabricam notícias no acervo. A suíte cobre corrupção, origem, idade, falhas, expiração, concorrência, proteção dos arquivos duráveis e edição idempotente pelo publicador existente.

Após merge, confirmar em Actions a execução do Scout, o artifact nomeado por run/tentativa, resumo de fontes e etapa de ausência de alterações. No próximo fechamento, conferir `snapshotRunId` e `snapshotCompletedAt` em `operation-state.json`. Uma edição pode ser retida legitimamente por falta de evidência ou mídia; restaurar o pool não autoriza publicação automática de qualquer candidato.

Nenhuma alteração em artigos permanentes, IDs, permalinks, frontend, APURANTE+, temas ou meteorologia. Manifestos independentes de edição, bundles mensais, loader histórico, URLs e política de âncoras ficam fora desta fase.
