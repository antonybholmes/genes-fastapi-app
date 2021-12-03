from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from database import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    genome = Column(String)
    assembly = Column(String)
    track = Column(String)
    description = Column(String)
    version = Column(String)


class DatabaseTrack(Track):
    db = Column(String)


class Gene(Base):
    __tablename__ = "genes"

    id = Column(Integer, primary_key=True, index=True)
    parent_gene = Column(Integer)
    parent_transcript = Column(Integer)
    type_id = Column(Integer, ForeignKey('types.id'))
    chr = Column(String)
    start = Column(Integer)
    end = Column(Integer)
    gene_id = Column(String)
    gene_name = Column(String)


class Name(Base):
    __tablename__ = "names"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type_id = Column(Integer, ForeignKey('types.id'))
    parent_gene = Column(Integer)


class Type(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)