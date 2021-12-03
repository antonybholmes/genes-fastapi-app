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

database = 'tracks.sqlite3'

sql_create_tracks_table = """ CREATE TABLE IF NOT EXISTS tracks (
                                        id INTEGER PRIMARY KEY,
                                        genome TEXT NOT NULL,
                                        assembly TEXT NOT NULL,
                                        track TEXT NOT NULL,
                                        description TEXT NOT NULL,
                                        version INTEGER NOT NULL,
                                        db TEXT NOT NULL
                                    ); """

sql_create_index_tracks = """CREATE INDEX IF NOT EXISTS idx_track ON genes (genome, assembly, track, version); """

conn = create_connection(database)

exec(conn, sql_create_tracks_table)
exec(conn, sql_create_index_tracks)

conn.commit()

conn.close()
