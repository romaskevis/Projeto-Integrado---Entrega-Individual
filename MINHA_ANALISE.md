# Crescimento demográfico — análise individual
**Bernardo Romaskevis · 3B2 · Python e Matemática · 2026**

## Objetivo e fonte
Apoiar os prefeitos de Curitiba, Porto Alegre, Belo Horizonte, Salvador e Florianópolis no planejamento de infraestrutura. Fonte: SIDRA 4709, Censo 2022, exportação recebida em 06/11/2026. População de 2010 compatibilizada com o território de 2022. Os dados originais e notas estão no XLSX anexo.

## Método reproduzível
`carregar()` lê todas as abas com Pandas, recupera cabeçalhos mesclados, preserva códigos, remove rodapés e duplicatas e transforma os dados para formato longo. Símbolos de ausência tornam-se NaN; o símbolo “-”, zero absoluto segundo o SIDRA, vira zero. Filtramos nível MU antes de calcular estatísticas. Não misturamos Brasil, regiões, estados e municípios.

`demografia()` une as três variáveis pela chave territorial e ano. População 2010 = população 2022 − variação absoluta. Crescimento acumulado = (população 2022 / população 2010 − 1) × 100. A taxa anual exibida vem diretamente do IBGE; não dividimos crescimento acumulado por 12. Denominadores não positivos não geram uma taxa válida.

## Resultados nacionais entre municípios
Foram analisadas 5570 unidades municipais, incluindo Brasília e Fernando de Noronha conforme a classificação do SIDRA. A média simples do crescimento acumulado foi **3.65%**; a mediana, **1.60%**. A média maior que a mediana indica influência de valores elevados. Essa média territorial não é a taxa de crescimento da população do Brasil.

| Medida | Resultado |
|---|---|
| n | 5570 |
| média | 3.65 |
| mediana | 1.60 |
| moda | 0.0 |
| Q1 | -4.68 |
| Q2 | 1.60 |
| Q3 | 9.03 |
| IQR | 13.71 |
| amplitude | 233.75 |
| variância populacional | 211.08 |
| desvio padrão populacional | 14.53 |
| limite inferior | -25.24 |
| limite superior | 29.59 |
| outliers | 279 |

Variância e desvio são populacionais (`ddof=0`), descrevendo o conjunto selecionado. A variância tem unidade (pontos percentuais)²; desvio, amplitude e IQR estão em pontos percentuais. Quartis usam interpolação linear. São mostradas todas as modas quando há repetição; sem repetição, a série é amodal.

## Capitais das personas
| territorio | pop2010 | pop2022 | crescimento_acumulado | taxa_anual |
|---|---|---|---|---|
| Salvador (BA) | 2675656.00 | 2417678.00 | -9.64 | -0.84 |
| Belo Horizonte (MG) | 2375609.00 | 2315560.00 | -2.53 | -0.21 |
| Curitiba (PR) | 1751907.00 | 1773718.00 | 1.24 | 0.10 |
| Florianópolis (SC) | 421240.00 | 537211.00 | 27.53 | 2.05 |
| Porto Alegre (RS) | 1409351.00 | 1332845.00 | -5.43 | -0.46 |

O crescimento é desigual: cidades que expandem precisam avaliar capacidade de saneamento, habitação e transporte; cidades que encolhem devem revisar uso da infraestrutura e distribuição de serviços. Esses são encaminhamentos de planejamento, não causas demonstradas pelos dados. Queda populacional, isoladamente, não prova envelhecimento.

## Outliers e decisão pública
A regra 1,5 × IQR definiu limites de -25.24% e 29.59%. Foram encontrados **279 extremos**, preservados na análise e listados em `outliers_municipais.csv`. Canaã dos Carajás (PA) apresentou 188,51% de crescimento acumulado e Catarina (CE), −45,24%. Esses casos pedem investigação de migração, economia e cobertura censitária antes de conclusões causais.

Sem os extremos, a média descritiva seria 1.79%, comparada a 3.65% com todos. A comparação ilustra sensibilidade; não justifica excluir observações reais.

## Limitações do cenário
A base não tem idade/sexo, portanto não mede envelhecimento e não sustenta pirâmide etária. Não há projeção oficial nem malha para mapa coroplético. Foram implementados ranking, boxplot, histograma, filtros e exportação; esses gráficos não substituem os itens específicos ausentes do cenário. Veja COBERTURA.md.

## Roteiro para apresentar e estudar
1. “Nossa consultoria usa o Censo para mostrar onde a população cresceu ou diminuiu.”
2. Mostre `carregar`: Pandas importa as planilhas; cada linha tratada representa um território, indicador, ano e sexo.
3. Mostre `demografia`: explique a reconstrução de 2010 e a fórmula de crescimento acumulado.
4. Mostre `estatisticas`: mediana é o centro; IQR é Q3 menos Q1; outlier ultrapassa os limites de 1,5 IQR.
5. No painel, selecione Municípios, depois uma região e uma capital. Explique que as estatísticas mudam com o filtro.
6. Compare Florianópolis e Salvador e apresente uma decisão de planejamento sustentada pelos números.
7. Explique as limitações e o que seria necessário para avaliar envelhecimento. Descreva sua participação e o apoio de ferramentas com honestidade.

Fonte: https://sidra.ibge.gov.br/tabela/4709
