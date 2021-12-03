
from fastapi import HTTPException
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
from models import Track, DatabaseTrack, Gene, Name


def get_tracks(db: Session):
    return db.query(Track).order_by(Track.genome, Track.assembly, Track.track, Track.version).all()


def get_track(db: Session,
              genome: str = 'Human',
              assembly: str = 'GRCh38',
              track: str = 'GENCODE',
              version: int = -1):

    print(genome, version)
    if version != -1:
        q = db.query(DatabaseTrack).filter(and_(func.lower(DatabaseTrack.genome) == func.lower(genome),
                                                func.lower(DatabaseTrack.assembly) == func.lower(
                                                    assembly),
                                                func.lower(
                                                    DatabaseTrack.track) == func.lower(track),
                                                Track.version == version))
    else:
        q = db.query(DatabaseTrack).filter(and_(func.lower(DatabaseTrack.genome) == func.lower(genome),
                                                func.lower(DatabaseTrack.assembly) == func.lower(
                                                    assembly),
                                                func.lower(DatabaseTrack.track) == func.lower(track))).order_by(desc(Track.version))

    if q.count() == 0:
        raise HTTPException(status_code=404, detail={
                            'message': 'Track not found', 'genome': genome, 'assembly': assembly, 'track': track, 'version': version})

    # if q.count() == 0:
    #     # perhaps we used an assembly synonym

    #     if assembly.lower() == 'hg19':
    #         return get_track(db, genome, 'GRCh37', track)
    #     elif assembly.lower() == 'mm10':
    #         return get_track(db, genome, 'GRCm38', track)
    #     elif assembly.lower() == 'mm39':
    #         return get_track(db, genome, 'GRCm39', track)
    #     else:
    #         pass

    return q.first()


def _order_genes(q):
    return q.order_by(Gene.parent_gene, Gene.parent_transcript, Gene.type_id, Gene.start)


def find(db: Session, chr: str, start: int, end: int):
    '''
    Find genes by position
    '''
    q = db.query(Gene).filter(and_(Gene.chr == chr, or_(and_(Gene.start >= start, Gene.end <= end), and_(
        Gene.start < start, Gene.end > start), and_(Gene.start < end, Gene.end > end))))

    return _order_genes(q).all()


def search(db: Session, search: str):
    '''
    Find genes by name
    '''
    q = db.query(Name).filter(Name.name.ilike(search))

    ids = [r.parent_gene for r in q.all()]

    q = db.query(Gene).filter(Gene.parent_gene.in_(ids))

    return _order_genes(q).all()
