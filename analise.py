"""ETL SIDRA: mantém níveis territoriais separados e unidades explícitas."""
from pathlib import Path
import numpy as np
import pandas as pd

REGIOES = {'1':'Norte','2':'Nordeste','3':'Sudeste','4':'Sul','5':'Centro-Oeste'}
COLUNAS=['tema','nivel','codigo','territorio','regiao','ano','sexo','indicador','unidade','valor']

def numero(v):
    if isinstance(v,str):
        if v.strip() in ['-']: return 0.0
        if v.strip() in ['...','..','X','']: return np.nan
        v=v.strip().replace('.','').replace(',','.') if ',' in v else v.strip()
    return pd.to_numeric(v,errors='coerce')

def carregar(arquivo):
    nome=str(getattr(arquivo,'name',arquivo))
    if nome.lower().endswith('.csv'):
        d=pd.read_csv(arquivo,sep=None,engine='python',encoding='utf-8-sig',dtype={'codigo':str})
        if not set(COLUNAS)<=set(d): raise ValueError('CSV deve seguir as colunas da base tratada fornecida.')
        d['valor']=d.valor.map(numero)
        d['ano']=pd.to_numeric(d.ano,errors='raise').astype(int)
        return d[COLUNAS].drop_duplicates()
    abas=pd.read_excel(arquivo,sheet_name=None,header=None)
    saida=[]
    for aba,t in abas.items():
        titulo=str(t.iloc[0,0])
        if not titulo.startswith('Tabela '): continue
        tabela=titulo.split()[1]
        if tabela not in ['4709','9694','7015','7135']: raise ValueError('Tabela SIDRA não suportada; use CSV tratado.')
        if str(t.iloc[2,0])!='Nível': raise ValueError('Exporte com códigos e siglas dos níveis territoriais, como os arquivos fornecidos.')
        tema={'4709':'Crescimento demográfico','9694':'Trabalho e emprego','7015':'Afazeres domésticos','7135':'Curso superior'}[tabela]
        anos=t.iloc[3].ffill()
        inicio=4 if tabela=='7135' else 3
        linha=4 if tabela=='4709' else 5
        nivel=codigo=territorio=None
        for _,r in t.iloc[linha:].iterrows():
            if pd.notna(r.iloc[0]):
                nivel=str(r.iloc[0]); codigo=str(r.iloc[1]); territorio=str(r.iloc[2])
            if nivel not in ['BR','GR','UF','MU']: continue
            for c in range(inicio,len(r),2):
                ano=numero(anos.iloc[c])
                if pd.isna(ano): continue
                val=numero(r.iloc[c])
                if pd.isna(val): continue
                sexo=str(t.iloc[4,c]) if tabela in ['9694','7015'] else 'Total'
                indicador=str(r.iloc[3]) if tabela=='7135' else str(t.iloc[1,0]).removeprefix('Variável - ')
                regiao=REGIOES.get(codigo[0],'Brasil') if nivel in ['UF','MU'] else (territorio if nivel=='GR' else 'Brasil')
                saida.append([tema,nivel,codigo,territorio,regiao,int(ano),sexo,indicador,str(r.iloc[c+1]),val])
    if not saida: raise ValueError('Nenhuma observação válida encontrada.')
    return pd.DataFrame(saida,columns=COLUNAS).drop_duplicates()

def demografia(d):
    p=d.pivot(index=['nivel','codigo','territorio','regiao','ano'],columns='indicador',values='valor').reset_index()
    p=p.rename(columns={'População residente':'pop2022','Variação absoluta da população residente 2010 compatibilizada':'variacao','Taxa de crescimento geométrico':'taxa_anual'})
    p['pop2010']=p.pop2022-p.variacao
    p['crescimento_acumulado']=np.where(p.pop2010>0,100*(p.pop2022/p.pop2010-1),np.nan)
    return p

def estatisticas(valores):
    x=pd.to_numeric(pd.Series(valores),errors='coerce').dropna()
    if x.empty: return {}
    q1,q2,q3=x.quantile([.25,.5,.75]); iqr=q3-q1
    lo,hi=q1-1.5*iqr,q3+1.5*iqr
    modas=x.mode().tolist() if x.value_counts().max()>1 else []
    return {'n':len(x),'média':x.mean(),'mediana':q2,'moda':', '.join(map(str,modas)) or 'Amodal','Q1':q1,'Q2':q2,'Q3':q3,'IQR':iqr,'amplitude':x.max()-x.min(),'variância populacional':x.var(ddof=0),'desvio padrão populacional':x.std(ddof=0),'limite inferior':lo,'limite superior':hi,'outliers':int(((x<lo)|(x>hi)).sum())}

def executar():
    raiz=Path(__file__).parent
    saida=raiz/'dados/tratados'; saida.mkdir(parents=True,exist_ok=True)
    for arq in (raiz/'dados/originais').glob('*.xlsx'):
        d=carregar(arq); d.to_csv(saida/(arq.stem+'.csv'),index=False,encoding='utf-8-sig')
        if arq.stem=='tabela4709': demografia(d).to_csv(saida/'crescimento_calculado.csv',index=False,encoding='utf-8-sig')
    print('ETL concluído.')
if __name__=='__main__': executar()
