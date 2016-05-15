# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 15:34:16 2016

@author: lukestarnes
"""

import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import plotly.tools as tls
import json


#TODO: https://github.com/amueller/word_cloud
#TODO: time over pages (month/year)
#TODO: Groupby for organizing book?



book_file = None
toc = None

class book_viz():
    def __init__(self, book_file, toc, p1, p2, places_json, people_json):
        print ('VIZ')
        py.sign_in('yg2bsm', '8e3m3cer5e')
        self.book_file = book_file
        self.toc = toc
        self.book_pivot1 = p1
        self.book_pivot2 = p2
        self.places_json = places_json
        self.people_json = people_json

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

    def places_vs_chapters(self):
        plotter_df = pd.DataFrame()
        num_chapters = max(self.book_pivot2.reset_index()['Chapter'])
        ch_list = list(range(1,num_chapters+1))
        for place_main in self.places_json:
            these_places = self.places_json[place_main]
            s = 'Word == "%s"'%(place_main)
            master_df = self.book_pivot2.query(s).reset_index().set_index('Chapter')
            master_df = master_df.reindex(ch_list).fillna(0)
            master_df['Word'] = place_main
            master_df.sort_index(inplace=True)
            del master_df['Book']
            for place_sub in these_places:
                s = 'Word == "%s"'%(place_sub)
                minor_df = self.book_pivot2.query(s).reset_index().set_index('Chapter')
                minor_df = minor_df.reindex(ch_list).fillna(0)
                minor_df.sort_index(inplace=True)
                del minor_df['Book']
                master_df['Count'] = master_df['Count'] + minor_df['Count']
        plotter_df = pd.concat([plotter_df,master_df])
        plotter_df = plotter_df.reset_index()
        plotter_df.set_index(['Chapter', 'Word'], inplace=True)
        self.plotter_df = plotter_df.unstack(level=1)
        self.plotter_df.iplot(fill=True, filename='cuflinks/filled-area')
        print ('learning')
        return self.plotter_df
