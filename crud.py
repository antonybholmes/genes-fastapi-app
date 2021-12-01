
import sys
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models import Gene, Track


def get_track(db: Session, genome: str, assembly: str, track: str):
    print(genome, assembly, track, file=sys.stderr)
    q = db.query(Track).filter(and_(Track.genome.ilike(genome),
                                    Track.assembly.ilike(assembly), Track.track.ilike(track)))

    if q.count() == 0:
        # perhaps we used an assembly synonym

        if assembly.lower() == 'hg19':
            return get_track(db, genome, 'GRCh37', track)
        elif assembly.lower() == 'mm10':
            return get_track(db, genome, 'GRCm38', track)
        elif assembly.lower() == 'mm39':
            return get_track(db, genome, 'GRCm39', track)
        else:
            pass

    return q.first()

def _order_genes(q):
    return q.order_by(Gene.track_id, Gene.parent_gene, Gene.parent_transcript, Gene.type_id, Gene.start)


def find(db: Session, Track: Track, chr: str, start: int, end: int):
    q = db.query(Gene).filter(and_(Gene.track_id == Track.id, Gene.chr == chr, or_(and_(Gene.start >= start, Gene.end <= end), and_(
        Gene.start < start, Gene.end > start), and_(Gene.start < end, Gene.end > end))))

    return  _order_genes(q).all()


def search(db: Session, Track: Track, search:str):
    q = db.query(Gene).filter(and_(Gene.track_id == Track.id, or_(Gene.gene_name.ilike(search), Gene.gene_id.ilike(search))))

    ids = [r.parent_gene for r in q.all()]

    q = db.query(Gene).filter(and_(Gene.track_id == Track.id, Gene.parent_gene.in_(ids)))

    return _order_genes(q).all()
