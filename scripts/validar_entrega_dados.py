"""Auditoria local independente do JSONL contra o CSV original, sem embeddings."""
import hashlib
import json
import platform
import re
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    raw_path = ROOT / 'data/raw/olist_order_reviews_dataset.csv'
    doc_path = ROOT / 'data/processed/reviews_documentos.jsonl'
    raw = pd.read_csv(raw_path, low_memory=False)
    docs = [json.loads(line) for line in doc_path.read_text(encoding='utf-8').splitlines()]
    clean = lambda v: '' if pd.isna(v) else re.sub(r'\s+', ' ', str(v)).strip()
    expected = {}
    for i, row in enumerate(raw.to_dict('records'), 1):
        parts = []
        for field, label in [('review_comment_title', 'Titulo'), ('review_comment_message', 'Comentario')]:
            value = clean(row[field])
            if value:
                parts.append(f'{label}: {value}')
        if parts:
            expected[f'olist_review_row_{i:06d}'] = ('\n'.join(parts), row)
    assert len(docs) == len(expected) == 42687
    assert len({d['id'] for d in docs}) == len(docs)
    for d in docs:
        text, row = expected[d['id']]
        m = d['metadata']
        assert set(d) == {'id', 'page_content', 'metadata'}
        assert d['page_content'] == text
        assert m['document_id'] == d['id']
        for field in ['review_id', 'order_id']:
            assert m[field] == clean(row[field])
        assert m['review_score'] == int(row['review_score'])
        assert m['review_creation_date'] == str(pd.to_datetime(row['review_creation_date']).date())
        assert m['fonte'] == raw_path.name
        assert m['hash_texto'] == hashlib.sha256(text.casefold().encode('utf-8')).hexdigest()
        assert m['n_palavras'] == len(text.split())
    groups = Counter(d['metadata']['hash_texto'] for d in docs)
    short = [d for d in docs if d['metadata']['n_palavras'] <= 3]
    # Content words exclude the labels inserted by the preprocessing pipeline.
    content_short = sum(len(re.sub(r'(?m)^(Titulo|Comentario): ', '', d['page_content']).split()) <= 3 for d in docs)
    baseline = json.loads((ROOT / 'reports/perfil_documentos_baseline.json').read_text(encoding='utf-8'))
    current = json.loads((ROOT / 'reports/perfil_documentos.json').read_text(encoding='utf-8'))
    assert current == baseline, 'Perfil documental diverge do checkpoint do Andre'
    report = {
        'data_execucao': '2026-11-04',
        'commit_origem': '1363122f6dcc00be6119b20404a04c1b6ce43a27',
        'python': platform.python_version(), 'pandas': pd.__version__,
        'avaliacoes_originais': len(raw), 'documentos_validados': len(docs),
        'perfil_identico_ao_checkpoint': True,
        'ids_unicos': True, 'textos_e_metadados_conferidos_com_origem': True,
        'textos_distintos': len(groups),
        'grupos_de_textos_repetidos': sum(n > 1 for n in groups.values()),
        'documentos_em_grupos_repetidos': sum(n for n in groups.values() if n > 1),
        'ocorrencias_adicionais_repetidas': sum(n - 1 for n in groups.values()),
        'maior_repeticao': max(groups.values()),
        'ate_3_palavras_incluindo_rotulos': len(short),
        'ate_3_palavras_sem_rotulos': content_short,
        'notas_dos_curtos': dict(Counter(str(d['metadata']['review_score']) for d in short)),
        'sha256_csv': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        'sha256_jsonl': hashlib.sha256(doc_path.read_bytes()).hexdigest(),
    }
    out = ROOT / 'reports/validacao_local_dados.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
