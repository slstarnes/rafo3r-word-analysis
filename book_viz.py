# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 15:34:16 2016

@author: lukestarnes
"""

import plotly

	
#TODO: https://github.com/amueller/word_cloud
#TODO: charecters over pages
#TODO: places over pages
#TODO: time over pages (month/year)
#TODO: Groupby for organizing book?



book_file = None
toc_df = None

class book_viz():
    def __init__(self, book_file, toc_df):
        print ('VIZ')