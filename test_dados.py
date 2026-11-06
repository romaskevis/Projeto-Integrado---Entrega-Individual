import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analise import *
ROOT=Path(__file__).resolve().parents[1]
class Dados(unittest.TestCase):
 def test_estatisticas(self):
  s=estatisticas([1,2,3,4,100])
  self.assertEqual(s['mediana'],3); self.assertEqual(s['IQR'],2); self.assertEqual(s['outliers'],1)
  self.assertEqual(s['moda'],'Amodal'); self.assertAlmostEqual(s['variância populacional'],1522)
 def test_populacao(self):
  d=carregar(ROOT/'dados/originais/tabela4709.xlsx'); p=demografia(d)
  br=p[p.nivel=='BR'].iloc[0]; uf=p[p.nivel=='UF']
  self.assertEqual(len(uf),27); self.assertEqual(len(p[p.nivel=='MU']),5570)
  self.assertEqual(uf.pop2022.sum(),br.pop2022)
  self.assertEqual(br.pop2010,190755799)
  self.assertAlmostEqual(br.crescimento_acumulado,100*12324957/190755799)
 def test_demais(self):
  d=carregar(ROOT/'dados/originais/tabela9694.xlsx')
  self.assertEqual(len(d[d.nivel=='UF']),27*2*3)
  self.assertEqual(d[(d.nivel=='BR')&(d.ano==2022)&(d.sexo=='Total')].valor.iloc[0],9.5)
  d=carregar(ROOT/'dados/originais/tabela7015.xlsx')
  self.assertEqual(len(d[d.nivel=='UF']),81)
  d=carregar(ROOT/'dados/originais/tabela7135.xlsx')
  self.assertEqual(len(d[d.nivel=='UF']),27*8*8)
 def test_csv(self):
  for n in [4709,9694,7015,7135]:
   a=carregar(ROOT/f"dados/originais/tabela{n}.xlsx")
   b=carregar(ROOT/f"dados/tratados/tabela{n}.csv")
   self.assertEqual(len(a),len(b)); self.assertEqual(set(a.columns),set(b.columns))
   self.assertAlmostEqual(a.valor.sum(),b.valor.sum())
 def test_numeros(self):
  self.assertEqual(numero('1.234,5'),1234.5); self.assertEqual(numero('7.3'),7.3)
  self.assertTrue(pd.isna(numero('...'))); self.assertEqual(numero('-'),0)
if __name__=='__main__': unittest.main()
