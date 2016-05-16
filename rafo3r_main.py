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
generate_toc_df = False
generate_pivots = False
generate_csvs = False
generate_ents = False
book_short_name = 'rafo3r'
places_json = json.loads(open('places.json', 'r',encoding='utf-8').read())
people_json = json.loads(open('people.json', 'r',encoding='utf-8').read())
rafo3r_reader = br.book_reader(book_short_name, generate_book_df,
                               generate_toc_df, generate_pivots)

book_file = 'rafo3r.txt'
h5_file = 'rafo3r.h5'

#if running on pythonanywhere
#book_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.txt'
#h5_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.h5'

rafo3r, toc, rafo3r_pivot1, rafo3r_pivot2  = rafo3r_reader.main(book_file, h5_file)

if generate_ents:
    rafo3r_reader.make_ents(book_file).to_csv(book_short_name + '_ents.csv')

if generate_csvs:
    now = str(dt.datetime.now())
    now = now.replace(':','')
    now = now.replace(' ','')
    now = now.replace('-','')
    now = now.replace('.','')
    rafo3r_reader.csv_dump(rafo3r,'rafo3r',now)
    rafo3r_reader.csv_dump(toc,'toc',now)
    rafo3r_reader.csv_dump(rafo3r_pivot1,'pivot1',now)
    rafo3r_reader.csv_dump(rafo3r_pivot2,'pivot2',now)

rafo3r_viz = bv.book_viz(rafo3r, toc, rafo3r_pivot1, rafo3r_pivot2,
                         places_json, people_json, rafo3r_reader.stopwords)

#########################################
#TODO: move this df making to _reader.
import pandas as pd
print('places_vs_chapters')
if False:
    places_vs_chapter_df = rafo3r_viz.word_vs_chapter_df_maker(rafo3r_pivot2, places_json, rafo3r_viz.ch_list, 400)
    places_vs_chapter_df.to_hdf(h5_file,'places_vs_chapter',format='table',append=False)
else:
    places_vs_chapter_df = pd.read_hdf(h5_file,'places_vs_chapter')

print('people_vs_chapters')
if False:
    people_vs_chapter_df = rafo3r_viz.word_vs_chapter_df_maker(rafo3r_pivot2, people_json, rafo3r_viz.ch_list, 100)
    people_vs_chapter_df.to_hdf(h5_file,'people_vs_chapter',format='table',append=False)
else:
    people_vs_chapter_df = pd.read_hdf(h5_file,'people_vs_chapter')

print('places_vs_range')
if False:
    places_vs_range_df = rafo3r_viz.word_vs_range_df_maker(rafo3r, places_json, 10000, 300)
    places_vs_range_df.to_hdf(h5_file,'places_vs_range',format='table',append=False)
else:
    places_vs_range_df = pd.read_hdf(h5_file,'places_vs_range')

print('people_vs_range')
if False:
    people_vs_range_df = rafo3r_viz.word_vs_range_df_maker(rafo3r, people_json, 10000, 100)
    people_vs_range_df.to_hdf(h5_file,'people_vs_range',format='table',append=False)
else:
    people_vs_range_df = pd.read_hdf(h5_file,'people_vs_range')

if True:
    now = str(dt.datetime.now())
    now = now.replace(':','')
    now = now.replace(' ','')
    now = now.replace('-','')
    now = now.replace('.','')
    rafo3r_reader.csv_dump(places_vs_chapter_df,'places_vs_chapter_df',now)
    rafo3r_reader.csv_dump(people_vs_chapter_df,'people_vs_chapter_df',now)
    rafo3r_reader.csv_dump(places_vs_range_df,'places_vs_range_df',now)
    rafo3r_reader.csv_dump(people_vs_range_df,'people_vs_range_df',now)
#########################################

print(rafo3r_viz.places_vs_chapters(places_vs_chapter_df))
print(rafo3r_viz.people_vs_chapters(people_vs_chapter_df))
#TODO: https://plot.ly/~yg2bsm/32/rafo3r-places-vs-10k-words/ shows no data
print(rafo3r_viz.places_vs_range(places_vs_range_df))
print(rafo3r_viz.people_vs_range(people_vs_range_df))
#TODO: https://plot.ly/%7Eyg2bsm/40/ (from table below) doesnt even load a graph
print(rafo3r_viz.people_table(people_vs_chapter_df))
