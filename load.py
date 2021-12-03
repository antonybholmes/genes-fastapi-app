# import matplotlib
# matplotlib.use('agg')
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd

# from fpdf import FPDF
import sqlite3
import re
import sys
import gzip

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    return sqlite3.connect(db_file)

def exec(conn, create_table_sql, c=None):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    if c is None:
        c = conn.cursor()

    try:
        c.execute(create_table_sql)
        #c.commit()
    except:
        print('Error s')


sql_create_meta_table = """ CREATE TABLE IF NOT EXISTS metadata (
                                        id INTEGER PRIMARY KEY,
                                        genome TEXT NOT NULL,
                                        assembly TEXT NOT NULL,
                                        track TEXT NOT NULL,
                                        description TEXT NOT NULL,
                                        version INTEGER NOT NULL
                                    ); """

sql_create_types_table = """ CREATE TABLE IF NOT EXISTS types (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL
                                    ); """

sql_create_genes_table = """ CREATE TABLE IF NOT EXISTS genes (
                                        id INTEGER PRIMARY KEY,
                                        parent_gene INTEGER NOT NULL,
                                        parent_transcript INTEGER NOT NULL,
                                        type_id INTEGER NOT NULL,
                                        chr TEXT NOT NULL,
                                        start INTEGER NOT NULL,
                                        end INTEGER NOT NULL,
                                        strand TEXT NOT NULL,
                                        gene_id TEXT NOT NULL,
                                        gene_name TEXT NOT NULL,
                                        FOREIGN KEY (type_id) REFERENCES types(id)
                                    ); """

sql_create_names_table = """ CREATE TABLE IF NOT EXISTS names (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL,
                                        type_id INTEGER NOT NULL,
                                        parent_gene INTEGER NOT NULL,
                                        FOREIGN KEY (type_id) REFERENCES types(id),
                                        FOREIGN KEY (parent_gene) REFERENCES genes(parent_gene)
                                    ); """

sql_create_index_genes = """CREATE INDEX IF NOT EXISTS idx_genes_track_chr_start_end ON genes (chr, start, end, parent_gene, parent_transcript, type_id); """
sql_create_index_gene_ids = """CREATE INDEX IF NOT EXISTS idx_genes_gene_id ON genes (gene_id); """
sql_create_index_gene_names = """CREATE INDEX IF NOT EXISTS idx_genes_gene_name ON genes (gene_name); """
sql_create_index_gene_parents = """CREATE INDEX IF NOT EXISTS idx_genes_sort ON genes (parent_gene, parent_transcript, type_id, start); """

sql_create_index_names = """CREATE INDEX IF NOT EXISTS idx_names ON names (name, type_id); """


genome = sys.argv[1]
assembly = sys.argv[2]
track = sys.argv[3]
description = sys.argv[4]
version = int(sys.argv[5])
gff = sys.argv[6]

db_file = f'genes_{genome.lower()}_{assembly.lower()}_{track.lower()}_{version}.sqlite3'


#
# First load entry into tracks db
#

conn = create_connection('tracks.sqlite3')

c = conn.cursor()

c.execute("SELECT id from tracks WHERE genome = ? AND assembly = ? AND track = ? AND version = ?", [genome, assembly, track, version])
track_id = c.fetchone()

if track_id is None:
    c.execute("INSERT INTO tracks (genome, assembly, track, description, version, db) VALUES(?, ?, ?, ?, ?, ?)", [genome, assembly, track, description, version, db_file])
    conn.commit()
    c.execute("SELECT id from tracks WHERE genome = ? AND assembly = ? AND track = ? AND version = ?", [genome, assembly, track, version])
    track_id = c.fetchone()

track_id = track_id[0]

conn.close()

# Now create database for gff

conn = create_connection(db_file)

c = conn.cursor()

exec(conn, sql_create_meta_table, c=c)
exec(conn, sql_create_types_table, c=c)
#exec(conn, sql_create_gene_names_table)
exec(conn, sql_create_genes_table, c=c)
exec(conn, sql_create_names_table, c=c)

exec(conn, sql_create_index_genes, c=c)
exec(conn, sql_create_index_gene_ids, c=c)
exec(conn, sql_create_index_gene_names, c=c)
exec(conn, sql_create_index_gene_parents, c=c)
exec(conn, sql_create_index_names, c=c)

c.execute("INSERT INTO types (name) VALUES(?)", ["Gene"])
c.execute("INSERT INTO types (name) VALUES(?)", ["Transcript"])
c.execute("INSERT INTO types (name) VALUES(?)", ["Exon"])

c.execute("INSERT INTO metadata (genome, assembly, track, description, version) VALUES(?, ?, ?, ?, ?)", [genome, assembly, track, description, version])

conn.commit()

# genome = "Human"
# assembly = "GRCh38"
# track = "GENCODE"
# version = "v27.basic"

# genome = "Human"
# assembly = "GRCh38"
# track = "GENCODE"
# version = "v38.basic"
# gff = "gencode.v38.basic.annotation.gff3.gz"

# genome = "Human"
# assembly = "hg19"
# track = "UCSC"
# version = "2020.01.11"
# gff = "ucsc_refseq_hg19_20200111.gtf.gz"


# genome = "Mouse"
# assembly = "GRCm38"
# track = "GENCODE"
# version = "M25.basic"
# gff = "gencode.vM25.basic.annotation.gff3.gz"


# genome = "Mouse"
# assembly = "GRCm39"
# track = "GENCODE"
# version = "M27.basic"
# gff = "gencode.vM27.basic.annotation.gff3.gz"


# genome = "Human"
# assembly = "GRCh37"
# track = "GENCODE"
# version = "38.basic"
# gff = "gencode.v38lift37.basic.annotation.gff3.gz"

print(f'db:{db_file}')
print(f'gff:{gff}')

f = gzip.open(gff, "r")

records = []
gene_names = []

ci = 1
gi = 0
ti = 0
ei = 0

gene = None
transcript = None
exon = None

for line in f:
    line = line.decode()
    if line.startswith("#"):
        continue

    line = line.replace(' "', '=').replace('"', '')

    tokens = line.strip().split("\t")

    chr = tokens[0]
    t = tokens[2]
    start = int(tokens[3])
    end = int(tokens[4])
    strand = tokens[6]
    loc = f'{chr}:{start}-{end}'

    if t == 'gene':
        gi += 1

        matcher = re.search(r'gene_name=(\w+)', tokens[8])
        gene_name = matcher.group(1)

        matcher = re.search(r'gene_id=([A-Z0-9\_\.]+)', tokens[8])
        gene_id = matcher.group(1)

        gene_names.append([gene_name, 1, gi])
        gene_names.append([gene_id, 1, gi])

        records.append([gi, -1, 1, chr, start, end, strand, gene_id, gene_name])

        
    elif t == 'transcript':
        ti += 1
        matcher = re.search(r'transcript_id=([A-Z0-9\_\.]+)', tokens[8])
        name = matcher.group(1)

        gene_names.append([name, 2, gi])

        records.append([gi, ti, 2, chr, start, end, strand, name, ''])
    elif t == 'exon':
        ei += 1
        matcher = re.search(r'exon_id=([A-Z0-9\_\.]+)', tokens[8])
        
        if matcher:
            name = matcher.group(1)
        else:
            name = f'EXON_{ei}'

        gene_names.append([name, 3, gi])

        records.append([gi, ti, 3, chr, start, end, strand, name, ''])
    else:
        pass

    if ci % 100000 == 0:
        print(f'Processed {ci}...')

    ci += 1

    #break

f.close()

print("Insert")
c.executemany("insert into names(name, type_id, parent_gene) values (?,?,?)", gene_names)
c.executemany("insert into genes(parent_gene, parent_transcript, type_id, chr, start, end, strand, gene_id, gene_name) values (?,?,?,?,?,?,?,?,?)", records)
conn.commit()

conn.close()