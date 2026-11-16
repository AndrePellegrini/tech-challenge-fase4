"""Conferência independente de artefatos, splits e referências do benchmark P1."""
import hashlib,json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
def read(path):return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
def require(condition,msg):
    if not condition:raise ValueError(msg)
def main():
    base=ROOT/'evaluation'; corpus=ROOT/'data/processed/reviews_documentos.jsonl'
    docs={d['id']:d for d in read(corpus)}
    manifest=json.loads((base/'manifesto_congelado.json').read_text(encoding='utf-8'))
    require(hashlib.sha256(corpus.read_bytes()).hexdigest()==manifest['corpus_sha256'],'Corpus alterado')
    for filename,expected in manifest['arquivos_sha256'].items():
        require(hashlib.sha256((base/filename).read_bytes()).hexdigest()==expected,'Arquivo alterado: '+filename)
    allcases=[]; hashes={}; counts={}
    for split,n in [('desenvolvimento',18),('teste_reservado',12)]:
        cases=read(base/split/'gabarito.jsonl'); questions=read(base/split/'perguntas.jsonl')
        require(len(cases)==len(questions)==n,'Quantidade incorreta')
        require([c['id'] for c in cases]==[q['id'] for q in questions],'Perguntas e gabarito divergentes')
        require(all(c['split']==split for c in cases),'Split incoerente')
        hashes[split]=set(); counts[split]=dict(Counter(c['tipo'] for c in cases))
        for case in cases:
            require(case['fatos'] and case['limites'],'Caso sem critério de avaliação')
            require(case['avaliacao_modelo']=='nao_executada','Caso com resultado fabricado')
            for e in case['evidencias_referencia']:
                original=docs[e['original_document_id']]
                require(e['trecho_suporte']==original['page_content'],'Trecho diferente do corpus')
                require(e['hash_texto_original']==original['metadata']['hash_texto'],'Hash de evidência inválido')
                require(e['review_score']==original['metadata']['review_score'],'Nota de referência divergente')
                hashes[split].add(e['hash_texto_original'])
        allcases.extend(cases)
    require(len({c['id'] for c in allcases})==30,'IDs repetidos')
    require(not(hashes['desenvolvimento']&hashes['teste_reservado']),'Evidência idêntica entre splits')
    require(Counter(c['tipo'] for c in allcases)=={'respondível':20,'insuficiente':4,'fora_escopo':3,'adversarial':3},'Composição incorreta')
    fixtures=read(base/'fixtures/contextos.jsonl')
    for f in fixtures:
        original=docs[f['original_document_id']]['page_content']
        require(f['page_content']==original or (f['sintetico'] and f['page_content'].startswith(original)),'Fixture sem proveniência')
    result={'data':'2026-11-07','casos':30,'composicao_por_split':counts,'referencias_exatas':True,
      'hashes_preservados':True,'evidencias_identicas_entre_splits':0,'fixture_sintetica_separada':True,
      'curadoria_humana':'pendente','avaliacao_gerador':'pendente; sem implementação executável de geração no checkpoint',
      'limite':'Teste reservado curado por IA e não usado para ajustar modelos; não é um teste cego com avaliador independente.'}
    path=ROOT/'reports/auditoria_benchmark_p1.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
