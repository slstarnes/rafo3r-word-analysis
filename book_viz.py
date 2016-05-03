# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 15:34:16 2016

@author: lukestarnes
"""

import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import plotly.tools as tls



	
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
        py.sign_in('yg2bsm', '8e3m3cer5e')
        self.book_file = book_file
        self.toc_df = toc_df
        
    def scat(self):
        germany = self.book_file[self.book_file['Words'] == 'germany']
        print (germany.head())
        data = [go.Scatter(x= germany.index, 
                           y=germany['Running Occurance'],
                           name='Germany')]
        layout = go.Layout(title='scatter plot with pandas',
                           yaxis=dict(title='random distribution'), xaxis=dict(title='linspace'))

        url = py.plot(data, filename='pandas/basic-line-plot')
        print (url)