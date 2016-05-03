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
toc = None

class book_viz():
    def __init__(self, book_file, toc, p1):
        print ('VIZ')
        py.sign_in('yg2bsm', '8e3m3cer5e')
        self.book_file = book_file
        self.toc = toc
        self.book_pivot1 = p1
        
    def scat(self):
        germany = self.book_file[self.book_file['Word'] == 'germany']
        print (germany.head())
        data = [go.Scatter(x= germany.index, 
                           y=germany['Running Count'],
                           name='Germany')]
        layout = go.Layout(title='scatter plot with pandas',
                           yaxis=dict(title='random distribution'), xaxis=dict(title='linspace'))

        url = py.plot(data, filename='pandas/basic-line-plot')
        print (url)
        
    def hist(self):
        #germany = self.book_file[self.book_file['Word'] == 'germany']
        #germany.hist(column="Count",by="Chapter",bins=30)
        pass