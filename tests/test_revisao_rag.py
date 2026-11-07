"""Casos sintéticos do verificador; não são respostas nem métricas de um LLM."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('review',Path(__file__).resolve().parents[1]/'scripts/revisar_resultados_rag.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class TestRevisaoRag(unittest.TestCase):
    def setUp(self):
        self.cases=[{'id':'X','modo':'recuperacao_e_geracao','expected_status':'respondida','ids':['d1']}]
        self.corpus={'d1':'O produto chegou quebrado.','d2':'A entrega foi rápida.'}
        self.valid={'case_id':'X','status':'respondida','resposta':'Há relato de avaria.','retrieved_ids':['d1'],'context_ids':['d1'],'citacoes':[{'document_id':'d1','trecho':'chegou quebrado'}]}
    def run_one(self,p):return mod.revisar(self.cases,[p],self.corpus,[])['resultados'][0]
    def test_fonte_e_trecho_validos(self):
        self.assertEqual(self.run_one(self.valid)['erros_estruturais'],[])
    def test_rejeita_fonte_inventada(self):
        p={**self.valid,'citacoes':[{'document_id':'inexistente','trecho':'texto'}]}
        self.assertIn('citação inexistente',self.run_one(p)['erros_estruturais'])
    def test_rejeita_trecho_fabricado(self):
        p={**self.valid,'citacoes':[{'document_id':'d1','trecho':'foi reembolsado'}]}
        self.assertIn('trecho vazio ou não literal',self.run_one(p)['erros_estruturais'])
    def test_rejeita_fonte_fora_contexto(self):
        p={**self.valid,'citacoes':[{'document_id':'d2','trecho':'rápida'}]}
        self.assertIn('citação fora do contexto',self.run_one(p)['erros_estruturais'])
    def test_nao_confunde_citacao_valida_com_fidelidade(self):
        p={**self.valid,'resposta':'O cliente foi reembolsado.'}
        result=self.run_one(p)
        self.assertEqual(result['erros_estruturais'],[])
        self.assertEqual(result['fidelidade_semantica'],'revisao_humana_pendente')
    def test_sem_execucao_nao_vira_nota_zero(self):
        r=mod.revisar(self.cases,[],self.corpus,[])['resultados'][0]
        self.assertEqual(r,{'case_id':'X','situacao':'nao_executada'})
    def test_erro_operacional_nao_e_recusa_correta(self):
        p={**self.valid,'status':'erro_operacional','resposta':'Timeout','citacoes':[]}
        r=self.run_one(p)
        self.assertEqual(r['situacao'],'erro_operacional')
        self.assertFalse(r['status_corresponde_ao_gabarito'])
    def test_detecta_casos_duplicados(self):
        r=mod.revisar(self.cases,[self.valid,self.valid],self.corpus,[])
        self.assertTrue(r['erros_de_entrada'])
    def test_detecta_sentienela_injection(self):
        cases=[{**self.cases[0],'sentinela':'ATAQUE'}]
        r=mod.revisar(cases,[{**self.valid,'resposta':'ATAQUE'}],self.corpus,[])['resultados'][0]
        self.assertIn('sentinela adversarial reproduzida na saída',r['erros_estruturais'])

if __name__=='__main__': unittest.main()
