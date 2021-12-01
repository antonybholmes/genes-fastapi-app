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

def exec(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except:
        print('Error s')

database = 'genedb.sqlite3'

sql_create_tracks_table = """ CREATE TABLE IF NOT EXISTS tracks (
                                        id INTEGER PRIMARY KEY,
                                        genome TEXT NOT NULL,
                                        assembly TEXT NOT NULL,
                                        track TEXT NOT NULL,
                                        version TEXT NOT NULL
                                    ); """

sql_create_types_table = """ CREATE TABLE IF NOT EXISTS types (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL
                                    ); """

sql_create_genes_table = """ CREATE TABLE IF NOT EXISTS genes (
                                        id INTEGER PRIMARY KEY,
                                        track_id INTEGER NOT NULL,
                                        parent_gene INTEGER NOT NULL,
                                        parent_transcript INTEGER NOT NULL,
                                        type_id INTEGER NOT NULL,
                                        chr TEXT NOT NULL,
                                        start INTEGER NOT NULL,
                                        end INTEGER NOT NULL,
                                        strand TEXT NOT NULL,
                                        annotation TEXT NOT NULL,
                                        FOREIGN KEY (track_id) REFERENCES tracks(id),
                                        FOREIGN KEY (type_id) REFERENCES types(id)
                                    ); """

sql_create_gene_names_table = """ CREATE TABLE IF NOT EXISTS gene_names (
                                        id INTEGER PRIMARY KEY,
                                        track_id INTEGER NOT NULL,
                                        name TEXT NOT NULL,
                                        name_type_id INTEGER NOT NULL,
                                        gene_id INTEGER NOT NULL,
                                        FOREIGN KEY (track_id) REFERENCES tracks(id),
                                        FOREIGN KEY (type_id) REFERENCES types(id),
                                        FOREIGN KEY (gene_id) REFERENCES genes(id)
                                    ); """

sql_create_index_genes = """CREATE INDEX IF NOT EXISTS idx_genes_track_chr_start_end ON genes (track_id, chr, start, end, parent_gene, parent_transcript, type_id); """
sql_create_index_gene_name_types = """CREATE INDEX IF NOT EXISTS idx_gene_name_types_name ON gene_name_types (name); """
sql_create_index_gene_names = """CREATE INDEX IF NOT EXISTS idx_gene_names_track_name ON gene_names (track_id, name); """

conn = create_connection(database)

exec(conn, sql_create_tracks_table)
exec(conn, sql_create_types_table)
exec(conn, sql_create_gene_names_table)
exec(conn, sql_create_genes_table)

exec(conn, sql_create_index_genes)
exec(conn, sql_create_index_gene_name_types)
exec(conn, sql_create_index_gene_names)

c = conn.cursor()

c.execute("INSERT INTO types (name) VALUES(?)", ["Gene"])
c.execute("INSERT INTO types (name) VALUES(?)", ["Transcript"])
c.execute("INSERT INTO types (name) VALUES(?)", ["Exon"])

conn.commit()

conn.close()