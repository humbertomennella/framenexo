---
{
  "articleId": "apr-2026-09-18-openai-hacktron-claude",
  "title": "Teste autorizado expõe falhas na OpenAI com ajuda do Claude",
  "description": "Pesquisadores da Hacktron AI encadearam vulnerabilidades em um teste autorizado, acessaram contas internas e receberam recompensa após relatar as falhas.",
  "quickTakeaways": [
    "A Hacktron AI realizou o teste dentro de um programa autorizado de recompensa por vulnerabilidades da OpenAI.",
    "O acesso começou por uma falha associada ao fórum de suporte e avançou para contas de funcionários e recursos internos.",
    "A OpenAI afirmou que corrigiu as vulnerabilidades relatadas; o caso reforça o uso de IA tanto na defesa quanto na descoberta de falhas."
  ],
  "publishedAt": "2026-09-19T02:15:00Z",
  "updatedAt": "2026-09-19T02:15:00Z",
  "category": "Tecnologia",
  "tags": ["Tecnologia","Cibersegurança","Inteligência Artificial","OpenAI","Claude"],
  "image": "/og.png",
  "imageAlt": "Arte institucional do APURANTE usada como capa editorial genérica.",
  "imageCredit": "Apurante Editorial",
  "status": "published",
  "confidence": "ALTA CONFIANÇA",
  "relevance": 95,
  "eventKey": "hacktron-openai-bug-bounty-18-setembro-2026",
  "editionId": "extraordinary:2026-09-19T02:15:00Z",
  "editionType": "extraordinary",
  "editionSlot": "2026-09-19T02:15:00Z",
  "editionLabel": "Edição extraordinária",
  "verificationPolicyVersion": 4,
  "sources": [
    {
      "name": "UOL",
      "url": "https://www.uol.com.br/tilt/noticias/redacao/2026/09/18/pesquisadores-dizem-ter-invadido-contas-do-chatgpt-em-teste-de-seguranca.ghtm",
      "publishedAt": "2026-09-18",
      "type": "press",
      "organization": "uol",
      "role": "reporting"
    },
    {
      "name": "The Guardian",
      "url": "https://www.theguardian.com/technology/2026/sep/18/openai-hacked-anthropic-claude-chatbot",
      "publishedAt": "2026-09-18",
      "type": "press",
      "organization": "guardian",
      "role": "reporting"
    },
    {
      "name": "TechCrunch",
      "url": "https://techcrunch.com/2026/09/18/researchers-used-anthropics-claude-to-hack-into-openai/",
      "publishedAt": "2026-09-18",
      "type": "press",
      "organization": "techcrunch",
      "role": "reporting"
    }
  ],
  "corrections": [],
  "author": "Apurante Editorial",
  "production": "Texto original produzido a partir de cobertura independente do UOL, The Guardian e TechCrunch, com separação entre o que foi demonstrado no teste autorizado e riscos hipotéticos.",
  "leadSourceOrganization": "uol",
  "slug": "teste-autorizado-expoe-falhas-openai-ajuda-claude"
}
---

Pesquisadores da startup de cibersegurança Hacktron AI conseguiram explorar vulnerabilidades em sistemas ligados à OpenAI durante um teste autorizado de segurança. O trabalho foi realizado dentro de um programa de recompensa por falhas, e não como uma invasão criminosa. UOL, The Guardian e TechCrunch relataram de forma independente o episódio nesta sexta-feira (18).

Segundo as reportagens, a equipe usou ferramentas de inteligência artificial, incluindo o Claude, da Anthropic, para acelerar partes da investigação. O ponto de entrada esteve relacionado ao fórum de suporte da OpenAI hospedado na plataforma Discourse. A partir dali, os pesquisadores conseguiram encadear falhas e alcançar contas de funcionários.

## O que os pesquisadores conseguiram acessar

A equipe afirmou ter obtido acesso a contas internas do ChatGPT e a recursos de desenvolvimento. O teste chegou ao ponto de permitir a criação de uma alteração inofensiva em documentação por meio do GitHub, usada pelos pesquisadores como demonstração de que a cadeia de acesso funcionava. As fontes consultadas convergem em um ponto importante: os pesquisadores interromperam o avanço quando perceberam o alcance potencial do acesso e comunicaram as vulnerabilidades à OpenAI.

A OpenAI confirmou que o trabalho ocorreu em contexto autorizado e recompensou a equipe com US$ 6,5 mil pelo relato das falhas. A empresa também informou que os problemas identificados foram corrigidos. Não há indicação, nas informações publicadas, de que código proprietário tenha sido copiado ou divulgado.

## Por que a IA foi relevante

O caso chama atenção menos pela existência de vulnerabilidades, algo esperado em programas de bug bounty, e mais pela velocidade com que ferramentas de IA foram incorporadas à investigação. Modelos como Claude foram usados para ajudar a organizar hipóteses, interpretar respostas de sistemas e acelerar tarefas que normalmente consumiriam mais tempo de uma equipe humana.

Isso não significa que a IA tenha realizado todo o ataque de forma autônoma. Os relatos descrevem pesquisadores humanos orientando o processo e decidindo quando avançar, parar e comunicar os achados. A distinção é importante porque demonstra o caráter de uso duplo dessas ferramentas: as mesmas capacidades que ajudam equipes defensivas a localizar falhas também podem reduzir o custo de operações ofensivas.

## O que o episódio demonstra

O incidente reforça uma mudança prática na área de cibersegurança: a automação baseada em IA está diminuindo o tempo necessário para pesquisar vulnerabilidades, correlacionar informações e testar caminhos de exploração. Isso aumenta a pressão sobre empresas de tecnologia para limitar privilégios, segmentar ambientes internos e tratar fóruns, sistemas de suporte e ferramentas de desenvolvimento como partes da mesma superfície de ataque.

Também mostra por que programas de recompensa continuam relevantes. Neste caso, a descoberta foi comunicada de forma coordenada, permitindo que a empresa corrigisse as falhas antes de uma exploração pública conhecida. Para equipes de segurança, o episódio reforça ainda a necessidade de revisar caminhos indiretos de autenticação, tokens reutilizados e integrações que, isoladamente, podem parecer pouco sensíveis.

## O que ainda não está demonstrado

As informações disponíveis não sustentam a conclusão de que modelos de IA estejam executando sozinhos ataques sofisticados contra grandes empresas. O episódio mostra que eles podem aumentar significativamente a capacidade de uma equipe humana, mas as decisões centrais do teste continuaram sob controle dos pesquisadores.

Essa diferença evita transformar um caso real de segurança em uma narrativa exagerada sobre autonomia total. O fato confirmado é mais concreto: pesquisadores usaram IA como multiplicador de produtividade em um teste autorizado que alcançou sistemas sensíveis, comunicaram os achados e tiveram as vulnerabilidades posteriormente corrigidas.
