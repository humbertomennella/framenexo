# Retomada da publicação editorial

O fechamento anterior rejeitava matérias comuns por pontuação legada: imprensa partia de 30 e precisava atingir 55 por palavras-chave. Também exigia mídia pré-vinculada antes de ligar o modelo, mas não possuía aquisição de mídia. O redator recebia apenas quatro fatos para produzir uma matéria longa.

## Mudanças

- Prioridade de recuperação não é confiança: uma reportagem não perde elegibilidade só por não conter as palavras-chave antigas. Rumor, opinião, fontes desativadas e datas inválidas continuam excluídos. Pontuações antigas do snapshot não bloqueiam a avaliação.
- Manchetes próximas são apenas candidatas ao cruzamento. Textos públicos devem sustentar explicitamente o mesmo núcleo factual, com trechos exatos e origem identificada em ao menos duas organizações. Divergência central ou origem incerta retém a pauta. Republicação detectada de agência conta como uma origem.
- A redação recebe evidência textual, não apenas quatro frases. Mantém revisão factual, antiplágio, datas/números ancorados, 9–12 parágrafos e 500–800 palavras úteis. O modelo local permanece restrito ao fechamento.
- Após validar o texto, o publicador pode buscar imagem específica no Wikimedia Commons. Aceita somente CC0 1.0, CC BY 4.0 ou CC BY-SA 4.0 com metadados explícitos de licença, autoria e página de origem. Não trata acesso público como autorização.
- Imagens adquiridas são identificadas como arquivo, não como fotografia do evento atual. A relação com o assunto é revisada a partir da descrição do arquivo. Não existe verificação visual infalível; na dúvida, a pauta é retida. A arte já publicada não é substituída.
- Direitos incluem origem, licença, escopo, prova obtida da API e SHA-256. Origem ou conteúdo já usado não pode ser repetido. Falta de mídia licenciada continua impedindo publicação; não existe gerador de imagens externo fictício no Actions.
- Imagens aprovadas entram no commit junto à matéria e aos direitos. O fechamento executa também Playwright antes de gravar a edição.
- Retenções têm motivos contados. Falhas temporárias não condenam automaticamente candidatos à quarentena permanente.

Scout permanece em Artifacts e com cron de 15 minutos. As quatro edições continuam às 08h, 13h, 18h e 22h de Brasília. Não há garantia de artigo em todo horário: duas rotas verificáveis, texto suficiente e direitos válidos continuam obrigatórios.

## Limites da primeira correção

A associação inicial ainda usa similaridade lexical e pode perder matérias em idiomas diferentes. O verificador é o modelo local, não revisão humana independente; confirmar trechos exatos não elimina erro de interpretação. Imagem de arquivo é julgada pela descrição e metadados, não por reconhecimento visual. APIs, robots.txt e fontes podem indisponibilizar conteúdos. Esses casos devem aparecer como retenção, nunca como publicação bem-sucedida.
