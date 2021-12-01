from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud

app = FastAPI()

@app.get('/about')
def get_about():
    return {'name':'genes', 'version':'6.0', 'copyright':'Copyright (C) 2014-2021 Antony Holmes'}


def _format_genes(track, genes, chr:str = '', s:int = -1, e:int = -1):
    ret = []

    current_gene = None
    current_transcript = None

    for gene in genes:
        if gene.type_id == 1:
            current_gene = {'id':gene.gene_id, 'c':gene.chr, 's':gene.start, 'e':gene.end, 'tr':[]}
            
            if gene.gene_name != '':
                current_gene['n'] = gene.gene_name

            ret.append(current_gene)
        if gene.type_id == 2:
            current_transcript = {'id':gene.gene_id, 'c':gene.chr, 's':gene.start, 'e':gene.end, 'ex':[]}
            
            if gene.gene_name != '':
                current_transcript['n'] = gene.gene_name

            current_gene['tr'].append(current_transcript)
        if gene.type_id == 3:
            current_exon = {'id':gene.gene_id, 'c':gene.chr, 's':gene.start, 'e':gene.end}

            if gene.gene_name != '':
                current_exon['n'] = gene.gene_name

            current_transcript['ex'].append(current_exon)

    ret = {'g':track.genome, 'a':track.assembly, 't':track.track, 'genes':ret}

    if chr != '':
        ret['c'] = chr
        ret['s'] = s
        ret['e'] = e

    return ret


@app.get('/find')
async def find_route(genome: str = 'Human', 
    assembly: str = 'grch38',
    track: str = 'gencode',
    chr: str = 'chr3',
    s: int = 187721377,
    e: int = 187736497,
    db: Session = Depends(get_db)):

    t = crud.get_track(db, genome, assembly, track)

    genes = crud.find(db, t, chr, s, e)

    return _format_genes(t, genes, chr, s, e)


@app.get('/search')
async def find_route(genome: str = 'Human', 
    assembly: str = 'grch38',
    track: str = 'gencode',
    q:str = 'BCL6',
    db: Session = Depends(get_db)):

    t = crud.get_track(db, genome, assembly, track)

    genes = crud.search(db, t, q)

    return _format_genes(t, genes)