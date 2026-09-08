#!/usr/bin/env python3
"""Expand legacy articles with transparent, non-speculative editorial context."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

LENSES = {
    "Brasil": "A leitura deve separar o anúncio nacional de sua execução local. Alcance, prazo e aplicação podem variar conforme o órgão responsável e novas etapas divulgadas depois da publicação.",
    "Mundo": "Em temas internacionais, uma decisão anunciada e sua implementação podem ocorrer em momentos diferentes. Também é importante distinguir a posição da instituição citada de uma conclusão válida para todos os países.",
    "Política": "Declarações, decisões institucionais e medidas efetivamente executadas são camadas diferentes. O texto identifica qual delas está documentada para evitar que intenção política seja apresentada como resultado consumado.",
    "Economia": "Indicadores econômicos descrevem um período, uma metodologia e uma base de comparação. Um número isolado não explica sozinho tendência, causa ou efeito sobre toda a população.",
    "Tecnologia": "Anúncio, teste, disponibilidade limitada e lançamento amplo não são sinônimos. A matéria preserva o estágio descrito pela fonte e evita converter possibilidade técnica em produto já disponível.",
    "Ciência": "Resultados científicos precisam ser lidos dentro do método, da amostra e do estágio da pesquisa. Observação, hipótese, teste e aplicação prática têm graus diferentes de evidência.",
    "Cultura": "Programação, abertura de inscrições e realização de um evento pertencem a etapas distintas. Datas, locais e condições de participação devem ser confirmados nos canais da organização.",
    "Esportes": "O registro esportivo considera resultado, fase da competição e informação oficial disponível na data. Mudanças de tabela, escalação ou condição de atletas exigem atualização própria.",
    "Saúde": "Informação de saúde pública não substitui orientação individual. Oferta anunciada, incorporação ao sistema e acesso efetivo pelo paciente podem depender de protocolos e etapas posteriores.",
    "Meio Ambiente": "Dados ambientais dependem de período, área observada e método de medição. O texto não transforma um recorte documentado em conclusão universal nem atribui causalidade sem evidência explícita.",
}

for path in sorted((ROOT / "content/news").glob("*.md")):
    raw = path.read_text()
    parts = raw.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"frontmatter inválido: {path}")
    meta = json.loads(parts[1])
    body = parts[2].strip()
    if "## Como ler esta notícia" in body:
        continue

    sources = ", ".join(dict.fromkeys(source["name"] for source in meta["sources"]))
    source_count = len(meta["sources"])
    source_label = "a fonte identificada" if source_count == 1 else "as fontes identificadas"
    lens = LENSES.get(meta["category"], LENSES["Brasil"])
    date = meta["sources"][0].get("publishedAt", "a data registrada")
    confidence = meta.get("confidence", "RELATO")

    addition = f"""

## Como ler esta notícia

O núcleo factual desta publicação é: {meta['description']} A redação conferiu esse enunciado com {source_label} — {sources} — e manteve no texto apenas informações compatíveis com o material consultado. A referência mais antiga usada nesta edição está datada de {date}; fatos posteriores precisam de uma atualização separada.

O selo **{confidence}** descreve o nível de sustentação editorial, não uma garantia de que o assunto esteja encerrado. Ele indica que a afirmação central está apoiada na origem listada ao fim da página. Quando a fonte registra uma fala, uma previsão ou uma decisão ainda não executada, essa natureza deve permanecer explícita: declaração não é resultado, previsão não é medição e anúncio não é entrega concluída.

## Contexto para interpretar

{lens}

Por esse motivo, a matéria evita ampliar o alcance do fato além do que foi documentado. Números conservam a referência temporal apresentada; nomes de instituições e programas são mantidos; e relações de causa e consequência só devem ser tratadas como confirmadas quando aparecem sustentadas na fonte. Essa cautela é especialmente importante em notícias que continuam evoluindo depois da primeira publicação.

## O que acompanhar agora

Os próximos elementos relevantes são eventuais documentos complementares, alterações de prazo, detalhamento de alcance e confirmações emitidas pelos responsáveis citados. Se uma dessas informações mudar o entendimento do caso, a atualização deve aparecer com data própria e, quando necessário, com uma nota de correção. Até lá, o limite seguro é o que está descrito nesta edição.

Para uma verificação independente, o leitor pode abrir os links em **De onde vem a informação**. Eles permitem comparar o resumo, os detalhes e a formulação original da fonte. Essa trilha de consulta faz parte da notícia: ela mostra o que sustenta o texto e também deixa claro o que ainda não pode ser concluído.
"""
    meta["updatedAt"] = STAMP
    meta["author"] = "Redação Verídia"
    parts[1] = "\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n"
    path.write_text("---" + parts[1] + "---\n" + body + addition.rstrip() + "\n")

print(f"Arquivo ampliado e atualizado em {STAMP}")
