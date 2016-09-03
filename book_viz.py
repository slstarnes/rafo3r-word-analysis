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
import PIL
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec

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
        self.places_vs_chapter = places_vs_chapter_df
        self.people_vs_chapter = places_vs_chapter_df
        self.places_vs_range = places_vs_chapter_df
        self.places_vs_chapter = places_vs_chapter_df
        self.places_json = places_json
        self.people_json = people_json
        self.stopwords = stopwords
        self.colors = [(191, 184, 162), (78, 77, 74), (148, 186, 101),
                       (153, 0, 0), (12, 99, 124), (39, 144, 176),
                       (230, 84, 0), (35, 68, 131),
                       (177, 140, 29), (116, 32, 104), (1, 137, 130),
                       (86, 87, 114), (163, 30, 57), (71, 100, 117),
                       (107, 121, 140), (235, 104, 37)]
        self.ch_list = list(range(1, max(self.places_vs_chapter.index) + 1))
        #remove last chapter (aftword)
        if self.ch_list[-1] == 33:
            self.ch_list = self.ch_list[:-1]
        assert (len(self.ch_list) == 32)
        self.word_cloud_init()


    # def scat(self):
    #     germany = self.book_file[self.book_file['Word'] == 'germany']
    #     print (germany.head())
    #     data = [go.Scatter(x= germany.index,
    #                        y=germany['Running Count'],
    #                        name='Germany')]
    #     layout = go.Layout(title='scatter plot with pandas',
    #                        yaxis=dict(title='random distribution'),
    #                        xaxis=dict(title='linspace'))

    #     url = py.plot(data, filename='pandas/basic-line-plot')
    #     print (url)

    def _col_clean(self, name):
        return name.replace('_', ' ').title()

    def _count_within_range(self, book_df, word, v0, v):
        return len(book_df[book_df['Position'] >=
                   v0][book_df['Position'] <
                   v][book_df['Word'] == word])

    def book_grapher(self, df, words_on_graph, entity_type, chapter_split,
                     chapter_markers = None, ipython = False):
        df = df[list(df.sum(axis=0).sort_values(ascending=False)
                     [:words_on_graph].index)]
        if chapter_split:
          #remove last chapter (aftword)
          if df[-1:].index == 33:
            df = df[:-1]
        else:
          if chapter_markers != None:
            pass
            #TODO: add this logic

        #set which items are hidden
        visibility_list = []
        for i in range(len(df.columns)):
            if i == 0:
                #for specific data the 1st element is quite large compared to
                #the rest, so this hides it so everything else doesn't appear
                #to be ~0.
                visibility_list.append('legendonly')
            elif 1 <= i <= 4:
                visibility_list.append('true')
            else:
                #4 lines seems to be a good number to show by default. this
                #hides the rest
                visibility_list.append('legendonly')

        colors = self.colors
        color_list = []
        for i in range(len(df.columns)):
            index = i - (len(colors) * int(i/len(colors)))
            this_color = colors[index]
            color_list.append('rgb(%i, %i, %i)'%(this_color[0],
                                                 this_color[1],
                                                 this_color[2]))

        new_col_names = list(map(self._col_clean, list(df.columns)))

        if entity_type == 'place':
          s1 = 'Places'
        elif entity_type == 'person':
          s1 = 'People'
        else:
          raise ValueError('Bad entity_type')

        if chapter_split:
          s2 = 'Chapter'
          xaxis=dict(title=s2,
                     tickvals=list(range(2, 36, 2)),
                     tickmode='array',
                     rangeslider=dict(thickness=0.2))
        else:
          s2 = 'Percentage'
          xaxis=dict(title=s2,
                     rangeslider=dict(thickness=0.2))

        plot_title = 'RaFo3R %s vs %s'%(s1,s2)
        file_name = 'plotly/%s_vs_%s'%(s1.lower(),s2.lower())

        plotly_dict = dict(data=[{
                             'x': df.index,
                             'y': df[col],
                             'name': new_col_names[i],
                             'visible': visibility_list[i],
                             'fill': 'none',
                             'hoverinfo': 'y+name',
                             'line': dict(color=(color_list[i]),
                                          width=4,
                                          smoothing=.8,
                                          shape="spline"),
                     } for i, col in enumerate(df.columns)],
                             layout=dict(title=plot_title,
                                     #autosize=False,
                                     #width=1800,
                                     #height=600,
                                     xaxis=xaxis,
                                     yaxis=dict(title='Word Count')))

        def opacity_lookup(i):
            #if i is divisible by 5, then opacity is 1 (solid line)
            #and if not then opacity <1 (transparant line)
            if i % 5 == 0:
                return 1
            else:
                return 0.4

        #plotly_dict.append()

        if not ipython:
          url = py.plot(plotly_dict, filename=file_name)
          return url
        else:
          this_plot = py.iplot(plotly_dict, filename=file_name)
          return this_plot

    def people_table(self, df, num_top_words, ipython = False):
        top_words = []

        for i in self.ch_list:
            top_words.append(list(df.loc[i].
                                  sort_values(ascending=False)
                                  [:num_top_words].index))
        top_words_df = pd.DataFrame(top_words, index=self.ch_list,
                                    columns=list(range(1, num_top_words + 1)))
        top_words_df = top_words_df.applymap(lambda x: x.title())

        if not ipython:
          url = py.plot(FF.create_table(top_words_df, index=True),
                        filename='plotly/top_people_table')
          return url
        else:
          this_plot = py.iplot(FF.create_table(top_words_df, index=True),
                        filename='plotly/top_people_table')
          return this_plot


    def word_cloud_init(self):
        self.people_list = (list(self.people_json.keys()) +
                       (list(chain.from_iterable(self.people_json.values()))))
        self.places_list = (list(self.places_json.keys()) +
                       (list(chain.from_iterable(self.places_json.values()))))

        assert len(self.people_list) == len(set(self.people_list))
        assert len(self.places_list) == len(set(self.places_list))
        assert list(set(self.people_list) & set(self.places_list)) == []

        self.book_full_list = list(self.book['Word'])
        self.book_people = list(self.book['Word']
                           [self.book['Word'].isin(list
                                                 (self.people_json.keys()))]
                           [self.book['Count'] > 1].apply(lambda x: x.title()))
        self.book_places = list(self.book['Word']
                           [self.book['Word'].isin(self.places_list)]
                           [self.book['Count'] > 1].apply(
                           lambda x: x.title().replace('_', '')))

        book_people_df = self.book.copy()
        book_people_df = book_people_df[book_people_df['Word'].isin(
                    list(self.people_json.keys()))][self.book['Count'] > 1]
        book_people_df['Word'] = book_people_df['Word'].apply(
                                                        lambda x: x.title())

        book_places_df = self.book.copy()
        book_places_df = book_places_df[self.book['Word'].isin(
                            self.places_list)][self.book['Count'] > 1]
        book_places_df['Word'] = book_places_df['Word'].apply(
                                        lambda x: x.title().replace('_', ''))

        self.book_full_dict = {}
        self.book_people_dict = {}
        self.book_places_dict = {}

        for ch in self.ch_list:
            self.book_full_dict[ch] = list(self.book['Word']
                                      [self.book['Chapter'] == ch])
            self.book_people_dict[ch] = list(book_people_df['Word']
                                        [book_people_df['Chapter'] == ch])
            self.book_places_dict[ch] = list(book_places_df['Word']
                                        [book_places_df['Chapter'] == ch])

    def _grey_color_func(self, word, font_size, position, orientation,
                        random_state=None, **kwargs):
        return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

    def make_word_clouds(self, full_cloud_filename, places_cloud_filename,
                         people_cloud_filename):
        book_df = self.book.copy()

        people_list = self.people_list
        places_list = self.places_list

        book_full_list = self.book_full_list
        book_people = self.book_people
        book_places = self.book_places

        book_wordcloud = WordCloud(width=1280, height=960,
                                   max_words=300,
                                   min_font_size=8,
                                   max_font_size=150,
                                   color_func=get_single_color_func('whitesmoke'),
                                   stopwords=self.stopwords).generate(''
                                   ' '.join(book_full_list))
        places_wordcloud = WordCloud(width=1280, height=960,
                                     max_words=300,
                                     min_font_size=8,
                                     max_font_size=150,
                                     color_func=get_single_color_func(
                                                            'sienna'),
                                     stopwords=self.stopwords).generate(
                                     ' '.join(book_places))
        people_wordcloud = WordCloud(width=1280, height=960,
                                     max_words=300,
                                     min_font_size=8,
                                     max_font_size=150,
                                     color_func=get_single_color_func('tan'),
                                     stopwords = self.stopwords).generate(
                                     ' '.join(book_people))

        #people_wordcloud.recolor(color_func=self._grey_color_func)

        book_wordcloud.to_file(full_cloud_filename)
        places_wordcloud.to_file(places_cloud_filename)
        people_wordcloud.to_file(people_cloud_filename)

    def word_cloud_matrix(self):
        book_df = self.book.copy()

        people_list = self.people_list
        places_list = self.places_list

        book_full_list = self.book_full_list
        book_people = self.book_people
        book_places = self.book_places

        for i, col in enumerate(people_vs_range_df.columns):
            ##need to use the toc to extract the words (using the ' '.join)
            ##for each chapter to make 33 little pictures...

            book_wordcloud = WordCloud(width=80,
                                       height=80,
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

            people_wordcloud.recolor(color_func=self._grey_color_func)

            #full_cloud_file = "full_cloud.png"
            #places_cloud_file = "places_cloud.png"
            #people_cloud_file = "people_cloud.png"
            #book_wordcloud.to_file(full_cloud_file)
            #places_wordcloud.to_file(places_cloud_file)
            #people_wordcloud.to_file(people_cloud_file)

    def matrix_cloud_maker(self, img_per_side=(1,1), image_inches=1, dpi=96,
                           book_dict=[], file_name='', color='darkred'):
        #assumes a list of dicts in the following format:
            #[{section_num : book_list_for_section},{section_num : book_list_for_section},...]
        width = ((img_per_side[0] * image_inches) +
                 (0.025 * (img_per_side[0]-1)))
        height = ((img_per_side[1] * image_inches) +
                  (0.025 * (img_per_side[1]-1)))
        fig = plt.figure(figsize=(width,height), dpi=dpi)
        fig.set_figwidth(width)
        fig.set_figheight(height)
        ax = [fig.add_subplot(img_per_side[0],
                              img_per_side[1],
                              i+1) for i in range(len(book_dict))]
        for num, book_list in book_dict.items():
            i = num - 1
            book_wordcloud = WordCloud(width=image_inches * dpi,
                                       height=image_inches * dpi,
                                       #max_words=300,
                                       min_font_size=8,
                                       #max_font_size=100,
                                       color_func=get_single_color_func(color),
                                       stopwords=self.stopwords).generate(
                                       ' '.join(book_list))
            ax[i].axis('off')
            ax[i].set_aspect('equal')
            #book_wordcloud.recolor(color_func=self._grey_color_func)
            ax[i].imshow(book_wordcloud.to_image())
        fig.subplots_adjust(wspace=0.025, hspace=0.025)
        plt.savefig(file_name, dpi=dpi)
        plt.close(fig)
