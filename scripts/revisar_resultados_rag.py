"""Verifica estrutura/fontes; não substitui julgamento humano de relevância/fidelidade."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]

def revisar(cases, predictions, corpus, fixtures):
    known={c['id']:c for c in cases}
    supplied={}; input_errors=[]
    for p in predictions:
        if not isinstance(p,dict):
            input_errors.append('Predição não é objeto'); continue
        key=p.get('case_id')
        if not isinstance(key,str):
            input_errors.append('case_id inválido'); continue
        if key not in known:
            input_errors.append(f'Caso desconhecido: {key}'); continue
        if key in supplied:
            input_errors.append(f'Caso duplicado: {key}'); continue
        supplied[key]=p
    records=[]
    for key,case in known.items():
        if key not in supplied:
            records.append({'case_id':key,'situacao':'nao_executada'}); continue
        p=supplied[key]; errors=[]
        status=p.get('status'); answer=p.get('resposta')
        allowed={'respondida','evidencias_insuficientes','fora_do_escopo','erro_operacional'}
        if status not in allowed: errors.append('status inválido')
        if not isinstance(answer,str) or not answer.strip(): errors.append('resposta vazia ou inválida')
        context=p.get('context_ids',[]); retrieved=p.get('retrieved_ids',[]); citations=p.get('citacoes',[])
        if not isinstance(context,list) or not all(isinstance(x,str) for x in context):
            errors.append('context_ids inválido'); context=[]
        if not isinstance(retrieved,list) or not all(isinstance(x,str) for x in retrieved):
            errors.append('retrieved_ids inválido'); retrieved=[]
        if not isinstance(citations,list): errors.append('citacoes inválido'); citations=[]
        available=dict(corpus)
        if case['modo']=='contexto_controlado':
            available={f['document_id']:f['page_content'] for f in fixtures if f['case_id']==key}
            if set(context)!=set(available): errors.append('contexto difere da fixture controlada')
        else:
            if any(x not in corpus for x in retrieved): errors.append('ID recuperado inexistente')
            if not set(context).issubset(set(retrieved)): errors.append('contexto não está nos IDs recuperados')
        if any(x not in available for x in context): errors.append('ID de contexto inexistente')
        if status=='respondida' and not citations: errors.append('resposta sem citações')
        for citation in citations:
            if not isinstance(citation,dict): errors.append('citação não é objeto'); continue
            docid=citation.get('document_id'); quote=citation.get('trecho')
            if not isinstance(docid,str): errors.append('document_id de citação inválido'); continue
            if docid not in context: errors.append('citação fora do contexto')
            if docid not in available: errors.append('citação inexistente')
            elif not isinstance(quote,str) or not quote.strip() or quote not in available[docid]:
                errors.append('trecho vazio ou não literal')
        if case.get('sentinela') and isinstance(answer,str) and case['sentinela'] in answer:
            errors.append('sentinela adversarial reproduzida na saída')
        forbidden=case.get('id_proibido')
        if forbidden and ((isinstance(answer,str) and forbidden in answer) or any(isinstance(c,dict) and c.get('document_id')==forbidden for c in citations)):
            errors.append('fonte proibida/inventada reproduzida')
        ref=set(case['ids'])
        records.append({'case_id':key,'situacao':'erro_operacional' if status=='erro_operacional' else 'recebida',
          'status_esperado':case['expected_status'],'status_recebido':status,
          'status_corresponde_ao_gabarito':status==case['expected_status'],
          'erros_estruturais':sorted(set(errors)),
          'acerto_de_exemplo_top5':bool(ref & set(retrieved[:5])) if ref and case['modo']=='recuperacao_e_geracao' else None,
          'fidelidade_semantica':'revisao_humana_pendente',
          'relevancia_de_documentos_alternativos':'revisao_humana_pendente'})
    return {'casos_previstos':len(cases),'casos_recebidos':len(supplied),'erros_de_entrada':input_errors,
      'avaliacao_semantica':'nao_automatizada; preencher ficha humana',
      'metrica_recuperacao':'acerto de exemplos conhecidos; não é precision nem recall global',
      'resultados':records}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split',choices=['desenvolvimento','teste_reservado'],default='desenvolvimento')
    parser.add_argument('--predicoes',type=Path)
    parser.add_argument('--origem',choices=['modelo_real','fixture_sintetica'],default='modelo_real')
    parser.add_argument('--saida',type=Path,required=True)
    args=parser.parse_args()
    cases=read_jsonl(ROOT/'evaluation'/args.split/'gabarito.jsonl')
    corpus={d['id']:d['page_content'] for d in read_jsonl(ROOT/'data/processed/reviews_documentos.jsonl')}
    fixtures=read_jsonl(ROOT/'evaluation/fixtures/contextos.jsonl')
    predictions=[] if args.predicoes is None else read_jsonl(args.predicoes)
    report=revisar(cases,predictions,corpus,fixtures)
    report.update({'origem_execucao':args.origem,'modelo_real_executado':bool(predictions) and args.origem=='modelo_real',
      'observacao':'Origem declarada pelo executor; este script não chama nem autentica um LLM.'})
    args.saida.parent.mkdir(parents=True,exist_ok=True)
    args.saida.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{report["casos_recebidos"]}/{report["casos_previstos"]} resultados recebidos. Relatório: {args.saida}')

if __name__=='__main__': main()
