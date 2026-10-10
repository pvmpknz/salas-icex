#!/usr/bin/env python3
"""Gera o site (index.html) a partir do PDF da grade de salas.

Uso:
    python gerar.py grade.pdf --semestre 2026/2

Precisa de: pip install -r requirements.txt
Arquivos usados: modelo.html (layout do site) e plantas/ (imagens das plantas).
Arquivo gerado: index.html
"""
import argparse, json, re, sys
from pathlib import Path
import pdfplumber

AQUI = Path(__file__).resolve().parent
DIAS = {'Seg': 1, 'Ter': 2, 'Qua': 3, 'Qui': 4, 'Sex': 5, 'Sáb': 6, 'Dom': 0}


def minutos(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def ler_pdf(caminho):
    """Lê a tabela (Matéria, Código, Turma, Início, Fim, Dias, Sala) de todas as páginas."""
    linhas, ignoradas = [], 0
    with pdfplumber.open(caminho) as pdf:
        for p in pdf.pages:
            for tabela in p.extract_tables():
                for r in tabela:
                    r = [(c or '').replace('\n', ' ').strip() for c in r]
                    if len(r) < 7 or r[0] == 'Matéria':
                        continue
                    mat, cod, tur, ini, fim, dias, sala = r[:7]
                    if not (re.fullmatch(r'\d\d:\d\d', ini) and re.fullmatch(r'\d\d:\d\d', fim)):
                        ignoradas += 1
                        continue
                    ds = [d.replace('Sab', 'Sáb') for d in re.split(r'[\s\-]+', dias) if d]
                    if not ds or any(d not in DIAS for d in ds):
                        ignoradas += 1
                        continue
                    linhas.append(dict(m=re.sub(r'\s+', ' ', mat), c=cod, t=tur, i=ini, f=fim,
                                       d=ds, s=re.sub(r'\s+', ' ', sala)))
    return linhas, ignoradas


def extrair_plantas(caminho):
    """Tenta salvar as 3 plantas da primeira página em plantas/1.jpg, 2.jpg, 3.jpg."""
    try:
        with pdfplumber.open(caminho) as pdf:
            imgs = [i for i in pdf.pages[0].images
                    if i['stream'].get('Filter') and 'DCT' in str(i['stream'].get('Filter'))
                    and i['srcsize'][0] >= 400]
            imgs.sort(key=lambda i: i['top'])
            if len(imgs) < 3:
                print('Aviso: não achei as 3 plantas no PDF; mantive as que já estão em plantas/.')
                return
            (AQUI / 'plantas').mkdir(exist_ok=True)
            for n, i in enumerate(imgs[:3], 1):
                (AQUI / 'plantas' / f'{n}.jpg').write_bytes(i['stream'].get_data())
            print('Plantas atualizadas.')
    except Exception as e:  # as plantas são opcionais
        print('Aviso: não consegui extrair as plantas (' + str(e) + '). Mantive as antigas.')


def atoms(loc):
    """return list of (id, name, group, order) for a location string"""
    l=re.sub(r'\s+',' ',loc).strip().rstrip('.')
    if l=='ON-LINE': return None
    if l=='1009 e 1010 - Laboratorio':
        return [('ICEx 1009 Lab','1009 · Laboratório','ICEx · 1º andar','1009'),('ICEx 1010 Lab','1010 · Laboratório','ICEx · 1º andar','1010')]
    m=re.fullmatch(r'CAD3 - (?:Sala )?(\d{3})(?: ENG)?',l)
    if m:
        n=m.group(1); g='CAD3 · 2º andar' if n[0]=='2' else ('CAD3 · 3º andar' if n[0]=='3' else 'CAD3 · 4º andar')
        return [('CAD3 '+n,'Sala '+n,g,n)]
    m=re.fullmatch(r'CAD3 - AUDITORIO B-(30\d)',l)
    if m: return [('CAD3 B'+m.group(1),'Auditório B-'+m.group(1),'CAD3 · Auditórios e laboratório','B'+m.group(1))]
    if l=='CAD3 - Auditorio B306': return [('CAD3 B306','Auditório B-306','CAD3 · Auditórios e laboratório','B306')]
    if l.startswith('CAD3 - LAICO B 307'): return [('CAD3 LAICO','LAICO B-307','CAD3 · Auditórios e laboratório','B307')]
    if l=='AUD. I - ICEX' or l=='AUD. I - QUI': return [('ICEx AUD1','Auditório I','ICEx · Auditórios','1')]
    if l=='AUD. II - ICEX': return [('ICEx AUD2','Auditório II','ICEx · Auditórios','2')]
    if 'Anexo I' in l:
        name=re.sub(r'\s*-?\s*Anexo I\s*-?\s*DQ','',l).strip(' -')
        name=re.sub(r'\s+',' ',name)
        name=re.sub(r'-\s*',', ',name)
        return [('Anexo '+name,'Labs '+name,'ICEx · Anexo I (Química)',name)]
    if l in ('1009 - Laboratorio','1010 - Laboratorio'):
        n=l[:4]; return [('ICEx %s Lab'%n,n+' · Laboratório','ICEx · 1º andar',n)]
    if l=='1001 - Lab. QUI': return [('ICEx 1001','1001 · Lab. Química','ICEx · 1º andar','1001')]
    if l in ('1027 - ENG','1027 - informatica'): return [('ICEx 1027','1027 · Informática','ICEx · 1º andar','1027')]
    if re.fullmatch(r'10\d\d',l): return [('ICEx '+l,l,'ICEx · 1º andar',l)]
    if l.startswith('2067-2068'): return [('ICEx 2052/2067','2052–2053 e 2067–2068 · Lab. Física','ICEx · 2º andar (Física)','2052')]
    m=re.fullmatch(r'(20(?:4\d|5\d|6\d|7\d)) e (20\d\d)',l)
    if m: return [('ICEx '+l,f'{m.group(1)} e {m.group(2)} · Lab. Física','ICEx · 2º andar (Física)',m.group(1))]
    if l in ('2051 LAB FIS','2055 - FIS'):
        n=l[:4]; return [('ICEx '+n,n+(' · Lab. Física' if n=='2051' else ' · Física'),'ICEx · 2º andar (Física)',n)]
    m=re.fullmatch(r'(2\d{3}|3\d{3}|4\d{3})(?: ?-? ?(MAT|DCC|EST|ENG|FIS|FISQ))?',l)
    if m and not l.startswith('2300') and not l.startswith('2307') and not l.startswith('2303'):
        n=m.group(1); dep={'2008':'MAT','2009':'DCC','2013':'DCC','2014':'DCC','2015':'DCC','2016':'DCC','2024':'EST','2032':'MAT','2033':'MAT','3048':'EST','3097':'FIS','3109':'MAT','4117':'FIS'}.get(n)
        label=n+(' · '+dep if dep else '')
        if n[0]=='2' and int(n)>=2042: g='ICEx · 2º andar (Física)'
        elif n[0]=='2': g='ICEx · 2º andar'
        else: g='ICEx · 3º e 4º andares'
        return [('ICEx '+n,label,g,n)]
    if l in ('3094 a 3096','3099','3102'):
        return [('ICEx '+l,l+' · Física' if l!='3102' else '3102','ICEx · 3º e 4º andares',l)]
    if l.startswith('ENG') or l.startswith('1166') or l.startswith('1177'):
        n=re.search(r'(\d{4})',l).group(1)
        blk=re.search(r'[Bb]loco (\d)',l); b=blk.group(1) if blk else ('4' if n[0] in '12' else '?')
        return [('ENG '+n,f'Eng. Bloco {b} · {n}','Engenharia',n)]
    if l=='2300 - ENG. BLOCO 4 º andar': return [('ENG 2300','Eng. Bloco 4 · 2300','Engenharia','2300')]
    if l.startswith('2307'): return [('ENG 2307','Eng. Bloco 4 · 2307','Engenharia','2307')]
    if l.startswith('2009 - ENG'): return [('ICEx 2009','2009 · DCC','ICEx · 2º andar','2009')]
    if l.startswith('CAD1') or l.startswith('CAD2'):
        n=re.sub(r'^(CAD\d) - (Sala )?','',l); p=l[:4]
        return [(l,f'{p} · {n}','CAD1 e CAD2',l)]
    return [(l, l, 'Outros locais', l)]


def montar(linhas):
    salas, online = {}, []
    for r in linhas:
        cls = dict(d=[DIAS[x] for x in r['d']], s=minutos(r['i']), e=minutos(r['f']), m=r['m'], c=r['c'], t=r['t'])
        at = atoms(r['s'])
        if at is None:
            online.append(cls)
            continue
        for id_, nome, grupo, ordem in at:
            sala = salas.setdefault(id_, dict(id=id_, n=nome, g=grupo, o=ordem, k=[]))
            sala['k'].append(cls)
    return dict(rooms=sorted(salas.values(), key=lambda x: (x['g'], x['o'])), online=online)


def main():
    ap = argparse.ArgumentParser(description='Gera o index.html a partir do PDF da grade.')
    ap.add_argument('pdf', help='caminho do PDF (ex.: grade.pdf)')
    ap.add_argument('--semestre', default='', help='rótulo mostrado no rodapé, ex.: 2026/2')
    a = ap.parse_args()

    linhas, ignoradas = ler_pdf(a.pdf)
    if not linhas:
        sys.exit('Não encontrei nenhuma linha de aula no PDF. O formato da tabela mudou?')
    dados = montar(linhas)
    extrair_plantas(a.pdf)

    outros = [r['n'] for r in dados['rooms'] if r['g'] == 'Outros locais']
    if outros:
        print('Atenção: locais que o script não reconheceu (aparecem em "Outros locais"):')
        for n in outros:
            print('  -', n)
        print('Se quiser organizar melhor, ajuste a função atoms() em gerar.py.')

    html = (AQUI / 'modelo.html').read_text(encoding='utf-8')
    js = json.dumps(dados, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = (html.replace('__DATA__', js).replace('__NROWS__', str(len(linhas)))
                .replace('__SEMESTRE__', a.semestre or 'atual'))
    (AQUI / 'index.html').write_text(html, encoding='utf-8')
    print(f"Pronto: {len(linhas)} horários, {len(dados['rooms'])} salas, {len(dados['online'])} turmas online "
          f"({ignoradas} linhas ignoradas). Abra index.html no navegador para conferir.")


if __name__ == '__main__':
    main()
