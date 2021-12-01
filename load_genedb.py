# import matplotlib
# matplotlib.use('agg')
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd

# from fpdf import FPDF
import numpy as np
import os
from svgwrite import gradients
import webcolors
from PIL import Image
import math
import sys
import sqlite3
import re
import json
import gzip
import bson

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    return sqlite3.connect(db_file)

database = 'genes.sqlite3'

# genome = "Human"
# assembly = "GRCh38"
# track = "GENCODE"
# version = "v27.basic"

genome = "Human"
assembly = "GRCh38"
track = "GENCODE"
version = "v27.basic"
gff = "gencode.v27.basic.annotation.gff3"

conn = create_connection(database)


f = open(gff, "r")

c = conn.cursor()

c.execute("SELECT id from tracks WHERE genome = ? AND assembly = ? AND track = ? AND version = ?", [genome, assembly, track, version])
track_id = c.fetchone()

if track_id is None:
    c.execute("INSERT INTO tracks (genome, assembly, track, version) VALUES(?, ?, ?, ?)", [genome, assembly, track, version])
    conn.commit()
    c.execute("SELECT id from tracks WHERE genome = ? AND assembly = ? AND track = ? AND version = ?", [genome, assembly, track, version])
    track_id = c.fetchone()

track_id = track_id[0]

records = []
gene_names = []

ci = 1
gi = 1
ti = 1

gene = None
transcript = None
exon = None

for line in f:
    if line.startswith("#"):
        continue

    tokens = line.strip().split("\t")

    chr = tokens[0]
    t = tokens[2]
    start = int(tokens[3])
    end = int(tokens[4])
    strand = tokens[6]
    loc = f'{chr}:{start}-{end}'

    #entity = {"chr":chr, "start":start, "end":end, "strand":strand}
    entity = {"loc":loc}

    if t == 'gene':
        matcher = re.search(r'gene_name=(\w+)', tokens[8])
        name = matcher.group(1)

        matcher = re.search(r'gene_id=([A-Z0-9\.]+)', tokens[8])
        alt_name = matcher.group(1)

        entity["st"] = strand
        entity["name"] = name
        entity["id"] = alt_name
        entity["tr"] = []

        gene = entity

        gene_names.append([track_id, name, 1, gi])
        gene_names.append([track_id, alt_name, 1, gi])

        records.append([track_id, -1, -1, 1, chr, start, end, gene["st"], alt_name, name])

        gi += 1
    elif t == 'transcript':
        matcher = re.search(r'transcript_id=([A-Z0-9\.]+)', tokens[8])
        name = matcher.group(1)

        entity["id"] = name
        entity["ex"] = []

        transcript = entity

        gene["tr"].append(transcript)
        gene_names.append([track_id, name, 2, gi])

        records.append([track_id, gi, -1, 2, chr, start, end, gene["st"], name, name])

        ti += 1
    elif t == 'exon':
        matcher = re.search(r'exon_id=([A-Z0-9\.]+)', tokens[8])
        name = matcher.group(1)

        matcher = re.search(r'exon_number=(\d+)', tokens[8])
        exon_number = int(matcher.group(1))

        entity["id"] = name
        entity["n"] = exon_number

        exon = entity

        transcript["ex"].append(exon)
        gene_names.append([track_id, name, 3, gi])

        records.append([track_id, gi, ti, 3, chr, start, end, gene["st"], name, name])
    else:
        pass

    if ci % 10000 == 0:
        print(f'Processed {ci}...')

    ci += 1

    #break

f.close()

jc = json.dumps(gene, separators=(',', ':'))
chr, r = gene["loc"].split(":")
start, end = [int(x) for x in r.split("-")]
records.append([track_id, chr, start, end, gene["st"], jc])

print("Insert")
c.executemany("insert into gene_names(track_id, name, name_type_id, gene_id) values (?,?,?,?)", gene_names)
c.executemany("insert into genes(track_id, parent_gene, parent_transcript, type_id, chr, start, end, strand) values (?,?,?,?,?,?,?,?)", records)
conn.commit()

conn.close()