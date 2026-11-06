from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from analise import carregar,demografia,estatisticas

ROOT=Path(__file__).parent
st.set_page_config(page_title='Números que Falam',page_icon='📊',layout='wide')
st.title('Números que Falam')
st.caption('Consultoria de dados públicos • Python e Matemática • IBGE')
TEMAS={'Crescimento demográfico':'4709','Trabalho e emprego':'9694','Afazeres domésticos':'7015','Curso superior':'7135'}
if (ROOT/'INDIVIDUAL').exists(): TEMAS={'Crescimento demográfico':'4709'}
tema=st.sidebar.selectbox('Indicador',list(TEMAS))
st.header(tema)
upload=st.sidebar.file_uploader('Substituir base: exportação SIDRA ou CSV tratado',type=['xlsx','csv'])
try:
    d=carregar(upload if upload else ROOT/f'dados/tratados/tabela{TEMAS[tema]}.csv')
    original=d.copy()
    if set(d.tema)!={tema}: raise ValueError('O tema do arquivo não corresponde ao módulo selecionado.')
except Exception as e:
    st.error(f'Não foi possível carregar: {e}'); st.stop()
niveis=[n for n in ['UF','MU','GR','BR'] if n in d.nivel.unique()]
nivel=st.sidebar.selectbox('Nível territorial',niveis,format_func=lambda x:{'UF':'Estados e DF','MU':'Municípios','GR':'Grandes regiões','BR':'Brasil'}[x])
d=d[d.nivel==nivel]
reg=st.sidebar.multiselect('Região',sorted(d.regiao.unique()),default=sorted(d.regiao.unique()))
d=d[d.regiao.isin(reg)]
if d.empty: st.info('Selecione ao menos uma região.'); st.stop()
if nivel=='MU':
    ufs=sorted(d.codigo.str[:2].unique())
    escolhidas=st.sidebar.multiselect('Código da UF',ufs,default=ufs)
    d=d[d.codigo.str[:2].isin(escolhidas)]
loc=st.sidebar.multiselect('Territórios (vazio = todos)',sorted(d.territorio.unique()))
if loc: d=d[d.territorio.isin(loc)]
ano=st.sidebar.selectbox('Ano',sorted(d.ano.unique()),index=len(d.ano.unique())-1)
sexo=st.sidebar.selectbox('Sexo',list(d.sexo.unique()))
d=d[d.sexo==sexo]
if d.empty: st.info('Sem dados para os filtros.'); st.stop()
if tema=='Crescimento demográfico':
    p=demografia(d)
    metrica=st.selectbox('Medida', ['crescimento_acumulado','taxa_anual','pop2022','variacao'],format_func=lambda x:{'crescimento_acumulado':'Crescimento acumulado 2010–2022 (%)','taxa_anual':'Crescimento médio anual oficial (%)','pop2022':'População 2022 (pessoas)','variacao':'Variação absoluta 2010–2022 (pessoas)'}[x])
    f=p[p.ano==ano].rename(columns={metrica:'valor'})
    unidade='pessoas' if metrica in ['pop2022','variacao'] else '%'
    st.caption('2010 compatibilizado = população de 2022 − variação absoluta. Crescimento acumulado = (2022/2010 − 1) × 100. Taxa anual é a publicada pelo IBGE.')
    capitais=['Curitiba','Porto Alegre','Belo Horizonte','Salvador','Florianópolis']
    if nivel=='MU':
        st.subheader('Capitais das personas no recorte')
        st.dataframe(f[f.territorio.str.replace(r' \(.*\)$','',regex=True).isin(capitais)],hide_index=True)
    limite='Sem idade/sexo na base: não é possível construir pirâmide etária ou medir envelhecimento. Não há projeção oficial anexada.'
elif tema=='Curso superior':
    p=d.pivot(index=['nivel','codigo','territorio','regiao','ano'],columns='indicador',values='valor').reset_index()
    if not {'Total','Superior completo'}<=set(p): st.error('Base deve conter Total e Superior completo.'); st.stop()
    p['valor']=100*p['Superior completo']/p['Total']; f=p[p.ano==ano]; unidade='%'
    st.caption('Percentual com superior completo entre pessoas de 25 anos ou mais. Razão de contagens em mil pessoas; não é taxa de conclusão de uma turma.')
    st.plotly_chart(px.line(p,x='ano',y='valor',color='territorio',markers=True,title='Evolução da proporção com superior completo'),use_container_width=True)
    limite='Arquivo contém apenas total de cor/raça, sem sexo ou área do conhecimento. Não permite responder ingresso, diplomação ou participação feminina em STEM.'
else:
    f=d[d.ano==ano]; unidade='%' if tema=='Trabalho e emprego' else 'horas'
    if tema=='Trabalho e emprego':
        p=d.pivot(index='territorio',columns='ano',values='valor')
        if {2012,2022}<=set(p):
            p['mudança (p.p.)']=p[2022]-p[2012]
            st.subheader('Comparação 2012–2022')
            st.dataframe(p.sort_values('mudança (p.p.)'),use_container_width=True)
            st.plotly_chart(px.bar(d,x='territorio',y='valor',color=d.ano.astype(str),barmode='group',labels={'color':'Ano','valor':'Desocupação (%)'}),use_container_width=True)
        limite='Taxa para pessoas de 15 anos ou mais. Queda da taxa não prova queda do número de desempregados. Não há contagens, rendimento, formalidade, setor ou escolaridade nesta tabela.'
    else:
        limite='Dados somente de 2022, por sexo. Não há raça, faixa etária, situação de ocupação ou série histórica nesse arquivo. As médias são agregadas, não horas individuais.'
        # Usa a cópia anterior aos filtros, sem reler o upload.
        g=original[(original.nivel==nivel)&original.territorio.isin(f.territorio)].pivot(index='territorio',columns='sexo',values='valor')
        if {'Homens','Mulheres'}<=set(g):
            g['Diferença mulheres − homens (horas)']=g.Mulheres-g.Homens
            st.subheader('Diferença de horas por sexo'); st.dataframe(g,use_container_width=True)
if f.empty: st.info('Sem observações nesse recorte.'); st.stop()
s=estatisticas(f.valor)
a,b,c,e=st.columns(4)
a.metric('Média territorial',f"{s['média']:.2f} {unidade}"); b.metric('Mediana',f"{s['mediana']:.2f} {unidade}"); c.metric('IQR',f"{s['IQR']:.2f}"); e.metric('Outliers',s['outliers'])
st.caption('Média simples entre os territórios selecionados, não estimativa nacional ponderada. Variância e desvio usam ddof=0; quartis por interpolação linear. Os níveis territoriais não são misturados.')
st.plotly_chart(px.bar(f.sort_values('valor',ascending=False).head(30),x='territorio',y='valor',labels={'valor':unidade,'territorio':'Território'},title='Comparação territorial — até 30 maiores valores'),use_container_width=True)
a,b=st.columns(2)
with a: st.plotly_chart(px.box(f,y='valor',points='outliers',labels={'valor':unidade},title='Distribuição entre territórios'),use_container_width=True)
with b: st.plotly_chart(px.histogram(f,x='valor',labels={'valor':unidade},title='Frequência de territórios'),use_container_width=True)
st.subheader('Estatísticas completas')
st.dataframe(pd.DataFrame({'Medida':list(s),'Resultado':[str(v) for v in s.values()]}),hide_index=True)
out=f[(f.valor<s['limite inferior'])|(f.valor>s['limite superior'])]
st.subheader('Valores extremos pela regra 1,5 × IQR'); st.dataframe(out,hide_index=True)
st.write(f"Média {s['média']:.2f} e mediana {s['mediana']:.2f}. Os {len(out)} extremos devem ser investigados; não são erros automaticamente. A comparação descreve os territórios e não estabelece causas.")
st.download_button('Baixar recorte analisado',f.to_csv(index=False).encode('utf-8-sig'),'recorte.csv','text/csv')
st.warning(limite)
with st.expander('Fontes e cobertura do trabalho'):
    st.markdown(f'[Fonte primária: SIDRA {TEMAS[tema]}](https://sidra.ibge.gov.br/tabela/{TEMAS[tema]})')
    st.markdown((ROOT/'COBERTURA.md').read_text(encoding='utf-8'))

st.subheader('Contexto e leitura complementar')
if tema=='Crescimento demográfico':
    st.image(str(ROOT/'imagens/capitais.png'),caption='Elaboração própria com a tabela 4709. Comparação fixa das cinco capitais das personas; não acompanha os filtros.')
    st.markdown('[IBGE Educa — População no Censo 2022](https://educa.ibge.gov.br/jovens/conheca-o-brasil/populacao/22005-censo-2022-o-retrato-atualizado-do-brasil.html)')
    st.caption('Contexto: o Censo permite comparar territórios e planejar serviços. Consulte as versões revisadas dos totais; notícias da primeira divulgação podem ter valores diferentes.')
elif tema=='Afazeres domésticos':
    st.markdown('[IBGE Educa — As mulheres do Brasil](https://educa.ibge.gov.br/jovens/materias-especiais/22052-as-mulheres-do-brasil)')
else:
    st.markdown('[Agência IBGE Notícias](https://agenciadenoticias.ibge.gov.br/) — consulte as divulgações do tema e confira o período de referência.')
