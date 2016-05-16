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

book_file = None
toc = None

class book_viz():
    def __init__(self, book, toc, p1, p2, places_json, people_json, stopwords):
        print ('VIZ')
        py.sign_in('yg2bsm', '8e3m3cer5e')
        self.book = book
        self.toc = toc
        self.book_pivot1 = p1
        self.book_pivot2 = p2
        self.places_json = places_json
        self.people_json = people_json
        self.stopwords = stopwords

        self.num_chapters = max(self.book_pivot2.reset_index()['Chapter'])
        self.ch_list = list(range(1,self.num_chapters+1))

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

    def _col_clean(self,name):
        return name.replace('_',' ').title()

    def _count_within_range(self, book_df, word, v0, v):
        return len(book_df[book_df['Position'] >= v][book_df['Position'] < v0][book_df['Word'] == word])

    def word_vs_range_df_maker(self, book_df, word_json, break_point = 10000, min_count_req = 400):
        peak = len(book_df)
        broken_list = list(range(0,peak,break_point))
        broken_list.pop(0)#remove 0
        if broken_list[-1] != peak: broken_list.append(peak)
        plotter_df = pd.DataFrame()
        for word_main in word_json:
            these_words = word_json[word_main]
            for i, v in enumerate(broken_list):
                if i == 0:
                    v0 = 0
                else:
                    v0 = broken_list[i-1]
                plotter_df.loc[str(v),word_main] = self._count_within_range(book_df,word_main,v0,v)
                for word_sub in these_words:
                    plotter_df.loc[str(v),word_main] += self._count_within_range(book_df,word_sub,v0,v)
        plotter_df = plotter_df.drop(plotter_df.sum(axis=0)
                                     [plotter_df.sum(axis=0)<min_count_req].index,axis=1)
        return plotter_df

    #using pivot2, create a new dataframe with words (subset based on places from json) as columns and chapter (counts)
    #as rows.
    def word_vs_chapter_df_maker(self, book_pivot2, word_json, ch_list, min_count_req = 400):
        bp2 = book_pivot2.copy()  #to my suprise, without this i was modifying the actual df (didnt think would happen in func)

        #######
        #TODO
        #remove this once you fix bug in pivot maker
        #print('P1',bp2.head())
        bp2.index = bp2.index.droplevel(1)
        bp2 = bp2[~bp2.index.duplicated(keep='first')]
        #print('P2',bp2.head())
        #######

        plotter_df = pd.DataFrame()
        for word_main in word_json:
            other_words = word_json[word_main]
            s = 'Word == "%s"'%(word_main)
            master_df = bp2.query(s).reset_index().set_index('Chapter')
            master_df = master_df.reindex(ch_list).fillna(0)
            master_df['Word'] = word_main
            master_df.sort_index(inplace=True)
            try:
                del master_df['Book']
            except:
                #remove this try once you fix the issue that lets you remove the stuff at start.
                #issue is that you remove book up there so you cant delete it here.
                pass
            for word_sub in other_words:
                s = 'Word == "%s"'%(word_sub)
                minor_df = bp2.query(s).reset_index().set_index('Chapter')
                minor_df = minor_df.reindex(ch_list).fillna(0)
                minor_df.sort_index(inplace=True)
                try:
                    del minor_df['Book']
                except:
                    #remove this try once you fix the issue that lets you remove the stuff at start.
                    #issue is that you remove book up there so you cant delete it here.
                    pass
                master_df['Count'] = master_df['Count'] + minor_df['Count']
            plotter_df = pd.concat([plotter_df,master_df])
        plotter_df = plotter_df.reset_index()
        plotter_df.set_index(['Chapter', 'Word'], inplace=True)
        plotter_df = plotter_df.unstack(level=1)
        plotter_df = plotter_df.drop(plotter_df.sum(axis=0)
                                     [plotter_df.sum(axis=0)<min_count_req].index,axis=1)
        plotter_df.columns = plotter_df.columns.droplevel(0)
        return plotter_df

    def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

    def make_word_clouds(self):
        from itertools import chain
        people_list = list(people_json.keys()) + (list(chain.from_iterable(people_json.values())))
        places_list = list(places_json.keys()) + (list(chain.from_iterable(places_json.values())))

        assert len(people_list) == len(set(people_list))
        assert len(places_list) == len(set(places_list))
        assert list(set(people_list) & set(places_list)) == []

        from wordcloud import WordCloud, get_single_color_func

        book_full_list = list(self.book['Word'])
        book_people = list(rafo3r['Word'][rafo3r['Word'].isin(list(people_json.keys()))]
                           [rafo3r['Count']>1].apply(lambda x: x.title()))
        book_places = list(rafo3r['Word'][rafo3r['Word'].isin(places_list)]
                           [rafo3r['Count']>1].apply(lambda x: x.title().replace('_','')))

        book_wordcloud = WordCloud(width = 1280, height = 960, max_words = 300,min_font_size = 8,
                                   max_font_size = 100,color_func = get_single_color_func('darkred'),
                                   stopwords = self.stopwords).generate(' '.join(book_full_list))
        places_wordcloud = WordCloud(width = 1280, height = 960, max_words = 200,min_font_size = 8,
                                     max_font_size = 150,color_func = get_single_color_func('lightsteelblue'),
                                     stopwords = self.stopwords).generate(' '.join(book_places))
        people_wordcloud = WordCloud(width = 1280, height = 960, max_words = 300,min_font_size = 8,
                              max_font_size = 100,color_func = get_single_color_func('darkred'),
                              stopwords = self.stopwords).generate(' '.join(book_people))


        #book_wordcloud.recolor(color_func=grey_color_func, random_state=3))

        full_cloud_file = "full_cloud.png"
        places_cloud_file = "places_cloud.png"
        people_cloud_file = "people_cloud.png"
        book_wordcloud.to_file(full_cloud_file)
        places_wordcloud.to_file(places_cloud_file)
        people_wordcloud.to_file(people_cloud_file)

    def places_vs_chapters(self):
        places_vs_chapter_df = self.word_vs_chapter_df_maker(self.book_pivot2, self.places_json, self.ch_list, 400)
        c = 256 / len(places_vs_chapter_df.columns)
        new_col_names = list(map(self._col_clean, list(places_vs_chapter_df.columns)))

        url = py.plot(dict(data=[{
                           'x': places_vs_chapter_df.index,
                           'y': places_vs_chapter_df[col],
                           'name': new_col_names[i],
                           'fill' : 'tonexty',
                           'line' : dict(color = ('rgb(%i, %i, 100)'%(int(c * i),int(255 - c * i)))),
                           }  for i, col in enumerate(places_vs_chapter_df.columns)],
                           layout=dict(title = 'RaFo3R Places vs Chapter',
                                       dragmode = 'zoom',
                                       xaxis = dict(title = 'Chapter',
                                                    tickvals = list(range(2,36,2)),
                                                    tickmode = 'array',
                                                    rangeslider = dict(thickness=0.2)),
                                       yaxis = dict(title = 'Word Count'))), filename='plotly/places_vs_chapter')
        return url

    def people_vs_chapters(self):
        people_vs_chapter_df = self.word_vs_chapter_df_maker(self.book_pivot2, self.people_json, self.ch_list, 100)
        c = 256 / len(people_vs_chapter_df.columns)
        new_col_names = list(map(self._col_clean, list(people_vs_chapter_df.columns)))

        url = py.plot(dict(data=[{
                           'x': people_vs_chapter_df.index,
                           'y': people_vs_chapter_df[col],
                           'name': new_col_names[i],
                           'fill' : 'tonexty',
                           'line' : dict(color = ('rgb(%i, %i, 100)'%(int(c * i),int(255 - c * i)))),
                           }  for i, col in enumerate(people_vs_chapter_df.columns)],
                           layout=dict(title = 'RaFo3R People vs Chapter',
                                       dragmode = 'zoom',
                                       xaxis = dict(title = 'Chapter',
                                                    tickvals = list(range(2,36,2)),
                                                    tickmode = 'array',
                                                    rangeslider = dict(thickness=0.2)),
                                       yaxis = dict(title = 'Word Count'))), filename='plotly/people_vs_chapter')
        return url

    def places_vs_range(self):
        places_vs_range_df = self.word_vs_range_df_maker(self.book, self.places_json, 10000, 300)
        c = 256 / len(places_vs_range_df.columns)
        new_col_names = list(map(self._col_clean, list(places_vs_range_df.columns)))

        url = py.plot(dict(data=[{
                           'x': list(places_vs_range_df.index).insert(0,'0'),
                           'y': places_vs_range_df[col],
                           'name': new_col_names[i],
                           'fill' : 'tonexty',
                           'line' : dict(color = ('rgb(%i, %i, 100)'%(int(c * i),int(255 - c * i)))),
                           }  for i, col in enumerate(people_vs_chapter_df.columns)],
                           layout=dict(title = 'RaFo3R Places vs 10k Words',
                                       dragmode = 'zoom',
                                       xaxis = dict(title = 'Per 10k Words',
                                                    rangeslider = dict(thickness=0.20)),
                                       yaxis = dict(title = 'Word Count'))), filename='plotly/places_vs_range')
        return url

    def people_vs_range(self):
        people_vs_range_df = self.word_vs_range_df_maker(self.book, self.people_json, 10000, 100)
        c = 256 / len(people_vs_range_df.columns)
        new_col_names = list(map(self._col_clean, list(people_vs_range_df.columns)))

        url = py.plot(dict(data=[{
                           'x': list(people_vs_range_df.index).insert(0,'0'),
                           'y': people_vs_range_df[col],
                           'name': new_col_names[i],
                           'fill' : 'tonexty',
                           'line' : dict(color = ('rgb(%i, %i, 100)'%(int(c * i),int(255 - c * i)))),
                           }  for i, col in enumerate(people_vs_chapter_df.columns)],
                           layout=dict(title = 'RaFo3R People vs 10k Words',
                                       dragmode = 'zoom',
                                       xaxis = dict(title = 'Per 10k Words',
                                                    rangeslider = dict(thickness=0.20)),
                                       yaxis = dict(title = 'Word Count'))), filename='plotly/people_vs_range')
        return url

    def people_table(self):
        people_vs_range_df = self.word_vs_range_df_maker(self.book, self.people_json, 10000, 100)
        top_words = []
        ch_range = range(1,self.num_chapters)

        num_top_words = 7

        for i in ch_range:
            top_words.append(list(people_vs_chapter_df.loc[i].sort_values(ascending=False)
                                  [:num_top_words].index))
        top_words_df=pd.DataFrame(top_words,index=list(ch_range),
                                  columns=list(range(1,num_top_words + 1)))
        url = py.plot(FF.create_table(top_words_df,index=True),
                      filename='plotly/top_people_table')
        return url

    def word_cloud_matrix():
        pass
