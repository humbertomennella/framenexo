# APURANTE — Estudo visual e sistema editorial 2026

## Objetivo

Este documento registra as decisões de interface adotadas para transformar o APURANTE em um portal de notícias de alta legibilidade, forte hierarquia editorial e boa experiência em desktop e celular, sem copiar a identidade de nenhum veículo existente.

## Princípios

1. **Leitura antes de decoração.** O conteúdo deve dominar a tela; bordas, sombras e cartões existem apenas quando ajudam a separar informação.
2. **Tema claro como padrão, escuro como opção.** Texto escuro sobre fundo claro favorece tarefas de leitura em estudos de polaridade visual. O tema escuro permanece disponível para preferência pessoal e uso noturno.
3. **Contraste mensurável.** Texto comum deve superar a referência WCAG AA de 4,5:1; informação importante não depende apenas de cor.
4. **Hierarquia de jornal, não de dashboard.** Uma manchete principal inequívoca, apoio lateral, notícias recentes e blocos por editoria.
5. **Densidade controlada.** A home pode exibir muitas notícias sem transformar tudo em cartões idênticos. Tamanho, tipografia, imagem e espaço definem prioridade.
6. **Mobile é uma composição própria.** No celular, a manchete fica em fluxo vertical, notícias recentes usam miniaturas compactas e cada editoria vira uma sequência simples de primeira e segunda leitura.
7. **Confiança visível.** Data, editoria, tempo de leitura, fontes, explicação editorial e tratamento de urgência devem ser fáceis de localizar.

## Paleta

### Tema claro padrão

| Papel | Cor | Uso |
|---|---|---|
| Fundo | `#F7F7F3` | Fundo geral levemente quente, reduz aspecto clínico |
| Superfície | `#FFFFFF` | Áreas que precisam de separação real |
| Texto | `#15181A` | Manchetes e corpo |
| Texto secundário | `#343A3F` | Descrições e apoio |
| Muted | `#586067` | Metadados |
| Verde APURANTE | `#315C0F` | Links, marcadores, foco de marca |
| Verde suave | `#E8F2DD` | Realce discreto |
| Urgente | `#B3262D` | Exclusivamente breaking news e alertas |

A identidade verde foi preservada, mas o tom de texto/acento é mais escuro no tema claro para assegurar contraste. O vermelho fica reservado para urgência; usá-lo em navegação comum reduziria seu valor semântico.

### Tema escuro opcional

Mantém o caráter original do APURANTE com fundo `#0A0C0F`, texto `#F4F6F2` e verde `#B4F564`, sem transformar o portal inteiro numa interface de aplicativo.

## Tipografia

- **Marca, navegação, metadados e corpo:** pilha sans-serif nativa do sistema para velocidade e clareza.
- **Manchetes editoriais:** pilha serifada nativa (`ui-serif`, Georgia, Cambria) para reforçar hierarquia jornalística e diferenciar título de interface.
- **Corpo da matéria:** aproximadamente `66ch`, `1.125rem` no desktop e line-height próximo de `1.72`.
- **Mobile:** corpo próximo de `1.055rem`, sem coluna lateral fixa.

## Estrutura da home

1. Faixa **URGENTE**, somente quando houver notícia realmente urgente.
2. **Manchete principal** com imagem dominante, título, resumo e acesso direto à matéria completa.
3. **EM FOCO** com até três pautas de alta relevância.
4. **Mais recentes**, com três matérias visuais e três chamadas textuais no desktop; lista compacta no celular.
5. **Eleições 2026**, tratada como cobertura especial.
6. Recursos de personalização sem competir com as manchetes.
7. Aviso de edição: quatro fechamentos diários e meta de 20 matérias verificadas.
8. Dez blocos de editoria, cada um preparado para **duas matérias**: primeira leitura visual e segunda leitura de apoio.
9. Diretório de editorias e elementos institucionais no final.

## Cards e imagens

- Cards de notícia não recebem sombra pesada nem bordas decorativas por padrão.
- Imagens principais usam proporção editorial horizontal; no mobile, notícias recentes usam miniaturas quadradas para economizar altura.
- Títulos e descrição nunca devem depender de texto sobre imagem para permanecer legíveis.
- A segunda matéria de uma editoria usa tratamento mais leve, deixando clara a prioridade sem esconder conteúdo.

## Página de matéria

- Título grande e serifado, linha de apoio e metadados antes da imagem.
- Imagem/capa editorial em largura controlada.
- **Leitura rápida** ao lado do texto no desktop e acima dele no celular.
- Corpo limitado a cerca de 66 caracteres médios por linha.
- Links no corpo são também sublinhados, não apenas coloridos.
- Fontes e transparência editorial ficam visíveis ao final.

## Responsividade

### Desktop

- Largura máxima aproximada de `1280px`.
- Hero em duas partes, com trilho de foco lateral.
- Três colunas para notícias recentes.
- Duas editorias por linha quando houver espaço.

### Tablet

- Hero passa para uma coluna principal.
- EM FOCO reorganiza as chamadas.
- Editorias passam para uma coluna.

### Celular

- Margens laterais compactas, sem texto espremido.
- Navegação horizontal rolável por editorias.
- Hero totalmente vertical.
- Últimas notícias em linhas com miniaturas compactas.
- Editorias em uma coluna, com separadores claros.
- Alvos interativos preservam dimensões adequadas para toque.

## Cronograma editorial

Fechamentos regulares em `America/Sao_Paulo`:

- **08h** — execução principal 08:07, recuperação 08:27.
- **13h** — execução principal 13:07, recuperação 13:27.
- **18h** — execução principal 18:07, recuperação 18:27.
- **22h** — execução principal 22:07, recuperação 22:27.

O Scout continua coletando fontes a cada 15 minutos. Cada edição tem meta de **20 matérias**, com alvo e teto de **2 por cada uma das 10 editorias**. A edição pode fechar abaixo de 20 somente quando não existirem vinte pautas que satisfaçam os critérios factuais e editoriais.

## Regra de qualidade

A cota nunca autoriza preencher espaço. Uma matéria só pode avançar com evidência suficiente, rota de fonte válida, revisão factual, deduplicação de evento, mídia permitida ou capa editorial própria e validação do site. Quantidade é objetivo operacional; precisão é requisito de publicação.
