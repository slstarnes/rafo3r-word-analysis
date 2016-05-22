# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 15:34:16 2016

@author: lukestarnes
"""

import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from plotly.tools import FigureFactory as FF
from itertools import chain
from wordcloud import WordCloud, get_single_color_func
import random

book_file = None
toc = None


class book_viz():
    def __init__(self, book, toc, wordvscount_pivot, wordchaptervscount_pivot,
                 wordbookvscount_pivot, places_vs_chapter_df,
                 people_vs_chapter_df, places_vs_range_df, people_vs_range_df,
                 places_json, people_json, stopwords):
        print('VIZ')
        py.sign_in('yg2bsm', '8e3m3cer5e')
        self.book = book
        self.toc = toc
        self.wordvscount_pivot = wordvscount_pivot
        self.wordchaptervscount_pivot = wordchaptervscount_pivot
        self.wordbookvscount_pivot = wordbookvscount_pivot
        #self.places_vs_chapter = places_vs_chapter_df
        #self.people_vs_chapter = places_vs_chapter_df
        #self.places_vs_range = places_vs_chapter_df
        #self.places_vs_chapter = places_vs_chapter_df
        self.places_json = places_json
        self.people_json = people_json
        self.stopwords = stopwords

    def scat(self):
        germany = self.book_file[self.book_file['Word'] == 'germany']
        print (germany.head())
        data = [go.Scatter(x= germany.index,
                           y=germany['Running Count'],
                           name='Germany')]
        layout = go.Layout(title='scatter plot with pandas',
                           yaxis=dict(title='random distribution'),
                           xaxis=dict(title='linspace'))

        url = py.plot(data, filename='pandas/basic-line-plot')
        print (url)

    def _col_clean(self, name):
        return name.replace('_', ' ').title()

    def _count_within_range(self, book_df, word, v0, v):
        return len(book_df[book_df['Position'] >=
                   v0][book_df['Position'] <
                   v][book_df['Word'] == word])

    def grey_color_func(self, word, font_size, position, orientation,
                        random_state=None, **kwargs):
        return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

    def make_word_clouds(self):
        book_df = self.book

        people_list = (list(self.people_json.keys()) +
                       (list(chain.from_iterable(self.people_json.values()))))
        places_list = (list(self.places_json.keys()) +
                       (list(chain.from_iterable(self.places_json.values()))))

        assert len(people_list) == len(set(people_list))
        assert len(places_list) == len(set(places_list))
        assert list(set(people_list) & set(places_list)) == []

        book_full_list = list(book_df['Word'])
        book_people = list(book_df['Word']
                           [book_df['Word'].isin(list
                                                 (self.people_json.keys()))]
                           [book_df['Count'] > 1].apply(lambda x: x.title()))
        book_places = list(book_df['Word']
                           [book_df['Word'].isin(places_list)]
                           [book_df['Count'] > 1].apply(
                           lambda x: x.title().replace('_', '')))

        book_wordcloud = WordCloud(width=1280,
                                   height=960,
                                   max_words=300,
                                   min_font_size=8,
                                   max_font_size=100,
                                   color_func=get_single_color_func('darkred'),
                                   stopwords=self.stopwords).generate(
                                   ' '.join(book_full_list))
        places_wordcloud = WordCloud(width=1280, height=960,
                                     max_words=200, min_font_size=8,
                                     max_font_size=150,
                                     color_func=get_single_color_func(
                                                            'lightsteelblue'),
                                     stopwords=self.stopwords).generate(
                                     ' '.join(book_places))
        people_wordcloud = WordCloud(width=1280, height=960,
                                     max_words=300, min_font_size=8,
                                     max_font_size=100,
                                     color_func=get_single_color_func('darkred'),
                                     stopwords = self.stopwords).generate(
                                     ' '.join(book_people))

        people_wordcloud.recolor(color_func=self.grey_color_func)

        full_cloud_file = "full_cloud.png"
        places_cloud_file = "places_cloud.png"
        people_cloud_file = "people_cloud.png"
        book_wordcloud.to_file(full_cloud_file)
        places_wordcloud.to_file(places_cloud_file)
        people_wordcloud.to_file(people_cloud_file)

    def places_vs_chapters_graph(self, places_vs_chapter_df, words_on_graph,
                                 drop_top_word=False):
        if drop_top_word:
            places_vs_chapter_df.drop(places_vs_chapter_df[
                                      list(places_vs_chapter_df.sum(axis=0).
                                      sort_values(ascending=False).index)].
                                      columns[[0]], axis=1, inplace=True)
        places_vs_chapter_df = places_vs_chapter_df[list(places_vs_chapter_df.
                                                         sum(axis=0).
                                                         sort_values(ascending=
                                                                     False)
                                                         [:words_on_graph].index)]

        #remove last chapter (aftword)
        places_vs_chapter_df = places_vs_chapter_df[:-1]

        c = 255 / len(places_vs_chapter_df.columns)
        new_col_names = list(map(self._col_clean,
                                 list(places_vs_chapter_df.columns)))

        url = py.plot(dict(data=[{
                           'x': places_vs_chapter_df.index,
                           'y': places_vs_chapter_df[col],
                           'name': new_col_names[i],
                           'fill': 'tonexty',
                           'line': dict(color=('rgb(%i, %i, 100)' %
                                              (int(c * i),
                                              int(255 - c * i)))),
                   } for i, col in enumerate(places_vs_chapter_df.columns)],
                           layout=dict(title='RaFo3R Places vs Chapter',
                                   dragmode='zoom',
                                   xaxis=dict(title='Chapter',
                                              tickvals=list(range(2, 36, 2)),
                                              tickmode='array',
                                              rangeslider=dict(thickness=0.2)),
                                   yaxis=dict(title='Word Count'))),
                      filename='plotly/places_vs_chapter')
        return url

    def people_vs_chapters_graph(self, people_vs_chapter_df, words_on_graph,
                                 drop_top_word=False):
        if drop_top_word:
            people_vs_chapter_df.drop(people_vs_chapter_df[
                                       list(people_vs_chapter_df.sum(axis=0).
                                       sort_values(ascending=False).index)].
                                       columns[[0]], axis=1, inplace=True)
        people_vs_chapter_df = people_vs_chapter_df[list(people_vs_chapter_df.
                                                     sum(axis=0).
                                                     sort_values(ascending=
                                                                 False)
                                                     [:words_on_graph].index)]
        #remove last chapter (aftword)
        people_vs_chapter_df = people_vs_chapter_df[:-1]

        c = 255 / len(people_vs_chapter_df.columns)
        new_col_names = list(map(self._col_clean,
                                 list(people_vs_chapter_df.columns)))

        url = py.plot(dict(data=[{
                           'x': people_vs_chapter_df.index,
                           'y': people_vs_chapter_df[col],
                           'name': new_col_names[i],
                           'fill': 'tonexty',
                           'line': dict(color=('rgb(%i, %i, 100)'%(int(c * i),int(255 - c * i)))),
                           } for i, col in enumerate(people_vs_chapter_df.columns)],
                           layout=dict(title = 'RaFo3R People vs Chapter',
                                       dragmode = 'zoom',
                                       xaxis = dict(title = 'Chapter',
                                                    tickvals = list(range(2,36,2)),
                                                    tickmode = 'array',
                                                    rangeslider = dict(thickness=0.2)),
                                       yaxis = dict(title = 'Word Count'))), filename='plotly/people_vs_chapter')
        return url

    def places_vs_range_graph(self, places_vs_range_df, words_on_graph,
                              drop_top_word=False):
        if drop_top_word:
            places_vs_range_df.drop(places_vs_range_df[
                                    list(places_vs_range_df.sum(axis=0).
                                         sort_values(ascending=False).index)].
                                    columns[[0]], axis=1, inplace=True)
        places_vs_range_df = places_vs_range_df[list(places_vs_range_df.
                                                     sum(axis=0).
                                                     sort_values(ascending=
                                                                 False)
                                                     [:words_on_graph].index)]

        #remove last chapter (aftword)
        places_vs_range_df = places_vs_range_df[:-1]

        c = 256 / len(places_vs_range_df.columns)
        new_col_names = list(map(self._col_clean,
                                 list(places_vs_range_df.columns)))

        url = py.plot(dict(data=[{
                           'x': list(places_vs_range_df.index).insert(0, '0'),
                           'y': places_vs_range_df[col],
                           'name': new_col_names[i],
                           'fill' : 'tonexty',
                           'line' : dict(color = ('rgb(%i, %i, 100)' %
                                                  (int(c * i),int(255 - c * i)))),
                           }  for i, col in enumerate(places_vs_range_df.columns)],
                           layout=dict(title = 'RaFo3R Places vs 10k Words',
                                       dragmode = 'zoom',
                                       xaxis = dict(title = 'Per 10k Words',
                                                    rangeslider = dict(thickness=0.20)),
                                       yaxis = dict(title = 'Word Count'))), filename='plotly/places_vs_range')
        return url

    def people_vs_range_graph(self, people_vs_range_df, words_on_graph,
                              drop_top_word=False):
        if drop_top_word:
            people_vs_range_df.drop(people_vs_range_df[
                                    list(people_vs_range_df.sum(axis=0).
                                    sort_values(ascending=False).index)].
                                    columns[[0]], axis=1, inplace=True)
        people_vs_range_df = people_vs_range_df[list(people_vs_range_df.
                                                sum(axis=0).
                                                sort_values(ascending=False)
                                                [:words_on_graph].index)]

        #remove last chapter (aftword)
        people_vs_range_df = people_vs_range_df[:-1]

        c = 256 / len(people_vs_range_df.columns)
        new_col_names = list(map(self._col_clean,
                                 list(people_vs_range_df.columns)))

        url = py.plot(dict(data=[{
                           'x': list(people_vs_range_df.index).insert(0, '0'),
                           'y': people_vs_range_df[col],
                           'name': new_col_names[i],
                           'fill': 'tonexty',
                           'line': dict(color=('rgb(%i, %i, 100)' %
                                              (int(c * i),
                                               int(255 - c * i)))),
                      } for i, col in enumerate(people_vs_range_df.columns)],
                            layout=dict(title = 'RaFo3R People vs 10k Words',
                                    dragmode = 'zoom',
                                    xaxis = dict(title = 'Per 10k Words',
                                        rangeslider = dict(thickness=0.20)),
                                        yaxis = dict(title = 'Word Count'))),
                            filename='plotly/people_vs_range')
        return url

    def people_table(self, people_vs_chapter_df, num_top_words):
        top_words = []

        num_chapters = max(people_vs_chapter_df.index)
        ch_list = list(range(1, num_chapters + 1))

        for i in ch_list:
            top_words.append(list(people_vs_chapter_df.loc[i].
                                  sort_values(ascending=False)
                                  [:num_top_words].index))
        top_words_df = pd.DataFrame(top_words, index=ch_list,
                                    columns=list(range(1, num_top_words + 1)))
        ###
        top_words_df.to_csv('top_words_df.csv')
        ###

        url = py.plot(FF.create_table(top_words_df, index=True),
                      filename='plotly/top_people_table')
        return url

    def word_cloud_matrix():
        #https://plot.ly/python/map-subplots-and-small-multiples/
        pass
