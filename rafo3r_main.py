# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 15:29:48 2016

@author: lukestarnes
"""

import book_reader as br
import book_viz as bv
import datetime as dt
import os
import json

generate_book_df = False 
generate_toc_df = True
generate_pivots = True
book_short_name = 'rafo3r'
places_json = json.loads(open('places.json', 'r').read())
people_json = json.loads(open('people.json', 'r').read())
my_reader = br.book_reader(book_short_name, generate_book_df, 
                           generate_toc_df, generate_pivots)

book_file = 'rafo3r.txt'
h5_file = 'rafo3r.h5'

#if running on pythonanywhere
#book_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.txt'
#h5_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.h5'    

rafo3r, toc, rafo3r_pivot1, rafo3r_pivot2  = my_reader.main(book_file, h5_file)

now = str(dt.datetime.now())
now = now.replace(':','')
now = now.replace(' ','')
now = now.replace('-','')
now = now.replace('.','')
my_reader.csv_dump(rafo3r,'rafo3r',now)
my_reader.csv_dump(toc,'toc',now)
my_reader.csv_dump(rafo3r_pivot1,'pivot1',now)
my_reader.csv_dump(rafo3r_pivot2,'pivot2',now)

#rafo3r_viz = bv.book_viz(rafo3r, toc, rafo3r_pivot1, rafo3r_pivot2, 
#                         places_json, people_json)
#rafo3r_viz.places_vs_chapters()


