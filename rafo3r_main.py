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

#TODO at the end:
#https://plot.ly/python/zoom-events/
#use JS to add a zoom capability
#and there is this...
#https://plot.ly/python/dropdowns/

generate_book_df = False
generate_toc_df = False
generate_pivots = False
generate_places_vs_chapter = False
generate_people_vs_chapter = False
generate_places_vs_range = False
generate_people_vs_range = True
generate_csvs = False
generate_ents = False
book_short_name = 'rafo3r'
places_json = json.loads(open('places.json', 'r', encoding='utf-8').read())
people_json = json.loads(open('people.json', 'r', encoding='utf-8').read())
rafo3r_reader = br.book_reader(book_short_name,
                               generate_book_df, generate_toc_df,
                               generate_pivots, generate_places_vs_chapter,
                               generate_people_vs_chapter,
                               generate_places_vs_range,
                               generate_people_vs_range,
                               places_json, people_json)
book_file = 'rafo3r.txt'
h5_file = 'rafo3r.h5'

#if running on pythonanywhere
#book_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.txt'
#h5_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.h5'

returned_list = rafo3r_reader.main(book_file, h5_file)
rafo3r = returned_list[0]
toc = returned_list[1]
rafo3r_wordvscount_pivot = returned_list[2]
rafo3r_wordchaptervscount_pivot = returned_list[3]
rafo3r_wordbookvscount_pivot = returned_list[4]
places_vs_chapter_df = returned_list[5]
people_vs_chapter_df = returned_list[6]
places_vs_range_df = returned_list[7]
people_vs_range_df = returned_list[8]

if generate_ents:
    rafo3r_reader.make_ents(book_file).to_csv(book_short_name + '_ents.csv')

if generate_csvs:
    now = str(dt.datetime.now())
    now = now.replace(':', '')
    now = now.replace(' ', '')
    now = now.replace('-', '')
    now = now.replace('.', '')
    rafo3r_reader.csv_dump(rafo3r, 'rafo3r', now)
    rafo3r_reader.csv_dump(toc, 'toc', now)
    rafo3r_reader.csv_dump(rafo3r_wordvscount_pivot,
                           'word_vs_count_pivot', now)
    rafo3r_reader.csv_dump(rafo3r_wordchaptervscount_pivot,
                           'wordchapter_vs_count_pivot', now)
    rafo3r_reader.csv_dump(rafo3r_wordbookvscount_pivot,
                           'wordbook_vs_count_pivot', now)
    rafo3r_reader.csv_dump(places_vs_chapter_df,
                           'places_vs_chapter', now)
    rafo3r_reader.csv_dump(people_vs_chapter_df,
                           'people_vs_chapter', now)
    rafo3r_reader.csv_dump(places_vs_range_df,
                           'places_vs_range', now)
    rafo3r_reader.csv_dump(people_vs_range_df,
                           'people_vs_range', now)

rafo3r_viz = bv.book_viz(rafo3r, toc, rafo3r_wordvscount_pivot,
                         rafo3r_wordchaptervscount_pivot,
                         rafo3r_wordbookvscount_pivot,
                         places_vs_chapter_df, people_vs_chapter_df,
                         places_vs_range_df, people_vs_range_df,
                         places_json, people_json, rafo3r_reader.stopwords)


#print (rafo3r_viz.book_grapher(places_vs_chapter_df, 10, 'place', True))
#print (rafo3r_viz.book_grapher(people_vs_chapter_df, 10, 'person', True))
#print (rafo3r_viz.book_grapher(places_vs_range_df, 10, 'place', False))
#print (rafo3r_viz.book_grapher(people_vs_range_df, 10, 'person', False))
#print(rafo3r_viz.people_table(people_vs_chapter_df, 7))
# rafo3r_viz.make_word_clouds()


rafo3r_viz.matrix_cloud_maker(img_per_side = (6,6), image_inches = 3,
                              dpi = 400,
                              book_dict = rafo3r_viz.book_full_dict,
                              file_name = 'rafo3r_matrix_cloud-2.png')
# rafo3r_viz.matrix_cloud_maker(img_per_side = (6,6), image_inches = 3,
#                               dpi = 400,
#                               book_dict = rafo3r_viz.book_people_dict,
#                               file_name = 'rafo3r_people_matrix_cloud-2.png')
# rafo3r_viz.matrix_cloud_maker(img_per_side = (6,6), image_inches = 3,
#                               dpi = 400,
#                               book_dict = rafo3r_viz.book_places_dict,
#                               file_name = 'rafo3r_places_matrix_cloud-2.png')

