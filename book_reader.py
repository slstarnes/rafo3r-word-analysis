# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import re
import datetime as dt


class book_reader():

    def __init__(self,
                 book_short_name,
                 generate_book_df=False,
                 generate_toc_df=False,
                 generate_pivots=False,
                 generate_places_vs_chapter=False,
                 generate_people_vs_chapter=False,
                 generate_places_vs_range=False,
                 generate_people_vs_range=False,
                 places_json=[],
                 people_json=[]):
        self.book_short_name = book_short_name
        self.generate_book_df = generate_book_df
        self.generate_toc_df = generate_toc_df
        self.generate_pivots = generate_pivots
        self.generate_places_vs_chapter = generate_places_vs_chapter
        self.generate_people_vs_chapter = generate_people_vs_chapter
        self.generate_places_vs_range = generate_places_vs_range
        self.generate_people_vs_range = generate_people_vs_range
        self.places_json = places_json
        self.people_json = people_json
        self.re_splitter = r'[;,.?†‡!"”()\]\[\*:\s\n]\s*'

        #Stopwords from http://www.lextek.com/manuals/onix/stopwords1.html
        #and github.com/amueller/word_cloud/blob/master/wordcloud/stopwords
        self.stopwords = list(set([x.strip()
                             for x in open('stopwords').read().split('\n')]))
        #my additions
        self.stopwords += ['', '-', '–','‡','†']

    def main(self, book_file, h5_file):

        print('Starting')
        if self.generate_book_df:
            book_df = self.process_book(book_file, h5_file)
        else:
            book_df = pd.read_hdf(h5_file, self.book_short_name)
        print('Book processed')
        if self.generate_toc_df:
            toc = self.process_toc(book_df, h5_file)
        else:
            toc = pd.read_hdf(h5_file, 'toc')
        print('TOC processed')
        if self.generate_book_df or self.generate_toc_df: ##if either one
            book_df = self.chapter_marker(h5_file)
        print('Chapter markers made')
        if self.generate_pivots:
            p1, p2, p3 = self.make_pivots(h5_file)
        else:
            p1 = pd.read_hdf(h5_file, self.book_short_name +
                             '_word_vs_count_pivot')
            p2 = pd.read_hdf(h5_file, self.book_short_name +
                             '_wordchapter_vs_count_pivot')
            p3 = pd.read_hdf(h5_file, self.book_short_name +
                             '_wordbook_vs_count_pivot')
        print('Pivots made')

        num_chapters = max(p2.reset_index()['Chapter'])
        ch_list = list(range(1, num_chapters + 1))

        if self.generate_places_vs_chapter:
            plvc = self.word_vs_chapter_df_maker(h5_file,
                                                 self.places_json,
                                                 'places_vs_chapter',
                                                 ch_list,
                                                 max_words=20)
        else:
            plvc = pd.read_hdf(h5_file, 'places_vs_chapter')
        print('Places v Chapter made')

        if self.generate_people_vs_chapter:
            pevc = self.word_vs_chapter_df_maker(h5_file,
                                                 self.people_json,
                                                 'people_vs_chapter',
                                                 ch_list,
                                                 max_words=100)
        else:
            pevc = pd.read_hdf(h5_file, 'people_vs_chapter')
        print('People v Chapter made')

        if self.generate_places_vs_range:
            plvr = self.word_vs_range_df_maker(h5_file,
                                               self.places_json,
                                               'places_vs_range',
                                               10000,
                                               max_words=20)
        else:
            plvr = pd.read_hdf(h5_file, 'places_vs_range')
        print('Places v Range made')

        if self.generate_people_vs_range:
            pevr = self.word_vs_range_df_maker(h5_file,
                                               self.people_json,
                                               'people_vs_range',
                                               10000,
                                               max_words=20)
        else:
            pevr = pd.read_hdf(h5_file, 'people_vs_range')
        print('People v Range made')

        return [book_df, toc, p1, p2, p3, plvc, pevc, plvr, pevr]

    def _de_possessive(self, word):
        if word.endswith("'s") or word.endswith("’s"):
            word = word[:-2]
        elif word.endswith("'") or word.endswith("’"):
            word = word[:-1]
        return word

    def _de_quote(self, word):
        if (word.startswith('"') or word.startswith('”') or
            word.startswith("'") or word.startswith("’")):
            word = word[1:]
        if (word.endswith('"') or word.endswith('”') or
            word.endswith("'") or word.endswith("’")):
            word = word[:-1]
        return word

    def _capitalization(self, word):
        if word.isdigit() or word.replace('.','').isdigit():
            return 'numeric'
        if re.match(r'^\$[0-9]*\.?[0-9]*', word):
            return 'currency'
        if word.isupper() or word.replace("'","").isupper():
            return 'upper'
        if word.istitle() or word.replace("'","").istitle():
            return 'title'
        if word.islower() or word.replace("'","").islower():
            return 'lower'
        else:
            return ''

    def _is_stop_word(self, word):
        if word.startswith('$'):
            return True
        elif word in self.stopwords:
            return True
        else:
            return False

    def csv_dump(self, df, file_name_extra1, file_name_extra2):
        file_name = file_name_extra1 + '_' + file_name_extra2 + '.csv'
        df.to_csv(file_name)

    def process_book(self, book_file, h5_file):
        bk = open(book_file, 'r', encoding='utf-8').read()

        book_list = re.split(self.re_splitter, bk)
        book_list = list(filter(None, book_list))  ## remove empty strings
        capitalization = list(map(self._capitalization, book_list))
        book_list = list(map(lambda s: s.lower(), book_list))
        book_list = list(map(self._de_quote, book_list))
        book_list = list(map(self._de_possessive, book_list))
        book_df = pd.DataFrame(book_list)
        book_df.rename(columns={0: 'Word'}, inplace=True)
        book_df['Stop Word'] = book_df['Word'].apply(self._is_stop_word)
        count = book_df['Word'][book_df['Stop Word'] ==
                                False].value_counts(sort=True)
        book_df['Capitalization'] = capitalization
        book_df['Count'] = 0
        book_df['Running Count'] = 0
        for w, c in count.iteritems():
            book_df.loc[book_df['Word'] == w, 'Count'] = c
            book_df.loc[book_df['Word'] ==
                                w, 'Running Count'] = list(range(1,c+1))
        book_df['Position'] = book_df.index + 1
        book_df.to_hdf(h5_file,
                       self.book_short_name,
                       format='table',
                       append=False)

        #simpler way
        #occurances = rafo3r.groupby('Word').size()
        #mega_words = occurances.index[occurances >= 1000]
        #rafo3r.index = rafo3r['Word']

        return book_df

    def process_toc(self, book_df, h5_file):
        maj_section_nums = ['One', 'Two', 'Three', 'Four', 'Five', 'Six']
        books = []
        for b in maj_section_nums:
            books.append('Book %s: '%(b))

        toc_ = [['B1', 'THE RISE OF ADOLF HITLER', 1],
               ['Ch1', 'BIRTH OF THE THIRD REICH', 3],
               ['Ch2', 'BIRTH OF THE NAZI PARTY', 27],
               ['Ch3', 'VERSAILLES, WEIMAR AND THE BEER HALL PUTSCH',  49],
               ['Ch4', 'THE MIND OF HITLER AND THE ROOTS OF THE THIRD REICH',  73],
               ['B2', 'TRIUMPH AND CONSOLIDATION', 102],
               ['Ch5', 'THE ROAD TO POWER: 1925-31',  103],
               ['Ch6', 'THE LAST DAYS OF THE REPUBLIC 1931-33',  133],
               ['Ch7', 'THE NAZIFICATION OF GERMANY: 1933-34',  167],
               ['Ch8', 'LIFE IN THE THIRD REICH: 1933-37',  205],
               ['B3', 'THE ROAD TO WAR', 245],
               ['Ch9', 'THE FIRST STEPS: 1934-37',  247],
               ['Ch10', 'STRANGE, FATEFUL INTERLUDE: THE FALL OF BLOMBERG, FRITSCH, NEURATH AND SCHACHT', 275],
               ['Ch11', 'ANSCHLUSS: THE RAPE OF AUSTRIA', 287],
               ['Ch12', 'THE ROAD TO MUNICH', 319],
               ['Ch13', 'CZECHOSLOVAKIA CEASES TO EXIST', 383],
               ['Ch14', 'THE TURN OF POLAND', 407],
               ['Ch15', 'THE NAZI-SOVIET PACT', 459],
               ['Ch16', 'THE LAST DAYS OF PEACE', 489],
               ['Ch17', 'THE LAUNCHING OF WORLD WAR II', 535],
               ['B4', 'WAR: EARLY VICTORIES AND THE TURNING POINT', 559],
               ['Ch18', 'THE FALL OF POLAND', 561],
               ['Ch19', 'SITZKRIEG IN THE WEST', 569],
               ['Ch20', 'THE CONQUEST OF DENMARK AND NORWAY', 605],
               ['Ch21', 'VICTORY IN THE WEST', 641],
               ['Ch22', 'OPERATION SEA LION: THE THWARTED INVASION OF BRITAIN', 681],
               ['Ch23', 'BARBAROSSA: THE TURN OF RUSSIA', 713],
               ['Ch24', 'A TURN OF THE TIDE', 767],
               ['Ch25', 'THE TURN OF THE UNITED_STATES', 783],
               ['Ch26', 'THE GREAT TURNING POINT: 1942 STALINGRAD AND EL ALAMEIN', 813],
               ['B5', 'BEGINNING OF THE END', 841],
               ['Ch27', 'THE NEW ORDER', 843],
               ['Ch28', 'THE FALL OF MUSSOLINI', 895],
               ['Ch29', 'THE ALLIED INVASION OF WESTERN EUROPE AND THE ATTEMPT TO KILL HITLER', 911],
               ['B6', 'THE FALL OF THE THIRD REICH', 972],
               ['Ch30', 'THE CONQUEST OF GERMANY', 973],
               ['Ch31', 'GOETTERDAEMMERUNG: THE LAST DAYS OF THE THIRD REICH', 993],
               ['Ch32', 'A BRIEF EPILOGUE', 1023],
               ['Ch33', 'AFTERWORD', 1027]]

        toc = pd.DataFrame(toc_)
        toc = toc.set_index(toc[0])
        del toc[0]
        toc.columns = ['Section Title', 'Page Num']
        toc.index.name = 'Section Num'

        toc['Location'] = 0

        book_df_iterator = book_df.iterrows()
        for toc_row in toc.iterrows():
            section_title = toc_row[1]['Section Title'].lower()
            section_title_split = re.split(self.re_splitter, section_title)

            section_id = toc_row[0]
            phrase = None
            if section_id.startswith('Ch'):
                phrase = ['chapter', section_id[2:]]
            elif section_id.startswith('B'):
                phrase = ['book',
                          maj_section_nums[int(section_id[1:]) - 1].lower()]

            section_title = ' '.join(section_title_split)
            section_title = ' '.join(phrase) + ' ' + section_title

            book_row = next(book_df_iterator)
            book_row_index = book_row[0]
            book_position = book_row[1]['Position']

            if book_row_index >= (len(book_df) - len(phrase) -
                                  len(section_title_split) + 1):
                break

            string_for_testing = None
            while string_for_testing != section_title:
                string_for_testing_list = []
                for i in range(len(section_title_split) + len(phrase)):
                    if book_row_index + i < len(book_df):
                        string_for_testing_list.append(book_df.at
                                                       [book_row_index + i,
                                                       'Word'])
                string_for_testing = ' '.join(string_for_testing_list)
                try:
                    book_row = next(book_df_iterator)
                    book_row_index = book_row[0]
                    book_position = book_row[1]['Position']
                except StopIteration:
                    #you have reached the end of the book, but you havent matched
                    #all of the sections.
                    #restart at the top of the book and move to the next section
                    print('Error. No matches found for %s'%section_id)
                    book_df_iterator = book_df.iterrows() #reset to top of book
                    break # move to the next toc_row

            else:
                #found the match for this section start
                toc.at[section_id, 'Location'] = book_position - 1

        toc.to_hdf(h5_file, 'toc', format='table', append=False)
        return toc

    def chapter_marker(self, h5_file):
        book_df = pd.read_hdf(h5_file, self.book_short_name)
        toc = pd.read_hdf(h5_file, 'toc')
        toc_books = toc[toc.index.str.startswith("B")]
        toc_chapters = toc[toc.index.str.startswith("Ch")]
        book_df['Book'] = np.searchsorted(toc_books['Location'],
                                          book_df['Position'])
        book_df['Chapter'] = np.searchsorted(toc_chapters['Location'],
                                             book_df['Position'])
        book_df.to_hdf(h5_file, self.book_short_name,
                       format='table', append=False)
        return book_df

    def make_pivots(self,h5_file):
        book_df = pd.read_hdf(h5_file, self.book_short_name)

        book_df_wordvscount_pt = book_df[book_df['Stop Word'] == False].pivot_table(
                                            values='Position',
                                            aggfunc=[len],
                                            index='Word')
        book_df_wordvscount_pt.sort_values('len',ascending=False, inplace=True)
        book_df_wordvscount_pt.rename(columns={'len': 'Count'}, inplace=True)

        book_df_wordchaptervscount_pt = book_df[book_df['Stop Word'] == False].pivot_table(
                                             values='Position',
                                             aggfunc=[len],
                                             index=['Word','Chapter'])
        book_df_wordchaptervscount_pt.sort_values('len',ascending=False, inplace=True)
        book_df_wordchaptervscount_pt.rename(columns={'len': 'Count'}, inplace=True)

        book_df_wordbookvscount_pt = book_df[book_df['Stop Word'] == False].pivot_table(
                                             values='Position',
                                             aggfunc=[len],
                                             index=['Word','Book'])
        book_df_wordbookvscount_pt.sort_values('len',ascending=False, inplace=True)
        book_df_wordbookvscount_pt.rename(columns={'len': 'Count'}, inplace=True)

        book_df_wordvscount_pt.to_hdf(h5_file, self.book_short_name +
                                      '_word_vs_count_pivot',
                          format='table',
                          append=False)
        book_df_wordchaptervscount_pt.to_hdf(h5_file, self.book_short_name +
                                             '_wordchapter_vs_count_pivot',
                           format='table',
                           append=False)
        book_df_wordbookvscount_pt.to_hdf(h5_file, self.book_short_name +
                                          '_wordbook_vs_count_pivot',
                           format='table',
                           append=False)

        return book_df_wordvscount_pt, \
               book_df_wordchaptervscount_pt, \
               book_df_wordbookvscount_pt


    def make_ents(self, book_file):
        import spacy
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load('en')
        book_nlp = nlp(book_file) #this creates a spacy.tokens.doc.Doc object
        book_ents = list(book_nlp.ents)

        ents_lists = []
        for ent in book_ents:
            ents_lists.append([ent.label, ent.label_,ent.orth_,ent.string])
        return pd.DataFrame(rafo3r_ents_lists,
                            columns=['Label ID', 'Label', 'Orth', 'String'])

    def _count_within_range(self, book_df, word, v0, v):
        return len(book_df[book_df['Position'] >= v0]
                   [book_df['Position'] < v][book_df['Word'] == word])

    def word_vs_range_df_maker(self, h5_file, word_json, h5_store_name,
                               break_point=10000, min_count_req=400,
                               max_words=0):
        book_df = pd.read_hdf(h5_file, self.book_short_name)

        wvc_pivot = pd.read_hdf(h5_file, self.book_short_name +
                                '_word_vs_count_pivot')
        word_list = list(word_json.keys())
        if max_words > 0:
            good_list = (wvc_pivot[wvc_pivot.index.isin(word_list)].
                         sort_values('Count')[-max_words:].index.values)
        else:
            good_list = (wvc_pivot[wvc_pivot.index.isin(word_list)][
                         wvc_pivot['Count'] >= min_count_req].index.values)

        peak = len(book_df)
        broken_list = list(range(0, peak,break_point))
        broken_list.pop(0)#remove 0
        if broken_list[-1] != peak:
            broken_list.append(peak)
        plotter_df = pd.DataFrame()
        for word_main in word_json:
            if word_main not in good_list:
                continue #restart for loop with new word
            these_words = word_json[word_main]
            for i, v in enumerate(broken_list):
                if i == 0:
                    v0 = 0
                else:
                    v0 = broken_list[i - 1]
                plotter_df.loc[str(v), word_main] = self._count_within_range(
                                                            book_df,
                                                            word_main,
                                                            v0, v)
                for word_sub in these_words:
                    plotter_df.loc[str(v),
                                   word_main] += self._count_within_range(
                                                              book_df,
                                                              word_sub,
                                                              v0, v)

        #Calculate location as percentage and set as index
        plotter_df['Percentage'] = list(plotter_df.index)
        plotter_df.index = plotter_df['Percentage'].apply(
                                      lambda x:format(100 * int(x) /
                                      max(book_df['Position']), '.2f'))
        del plotter_df['Percentage']

        if max_words == 0:
            plotter_df = plotter_df.drop(plotter_df.sum(axis=0)
                                         [plotter_df.sum(axis=0) <
                                          min_count_req].index, axis=1)
            #sort columns by total word count
            plotter_df = plotter_df[plotter_df.sum(axis=0).sort_values(
                                                   ascending=False).index]
        else:
            plotter_df = plotter_df[list(plotter_df.sum(axis=0).
                                         sort_values(ascending=False)
                                         [-max_words:].index)]

        plotter_df.to_hdf(h5_file, h5_store_name,format='table', append=False)

        return plotter_df

    #using word/chapter vs count pivot, create a new dataframe with words
    #(subset based on places from json) as columns and chapter (counts) as rows
    def word_vs_chapter_df_maker(self, h5_file, word_json, h5_store_name,
                                 ch_list, min_count_req=400, max_words=0):
        wcvc_pivot = pd.read_hdf(h5_file, self.book_short_name +
                                 '_wordchapter_vs_count_pivot')

        wvc_pivot = pd.read_hdf(h5_file, self.book_short_name +
                                '_word_vs_count_pivot')

        #shorten the json to the minimum needed per inputs
        word_list = list(word_json.keys())
        if max_words > 0:
            good_list = (wvc_pivot[wvc_pivot.index.isin(word_list)].
                         sort_values('Count')[-max_words:].index.values)
        else:
            good_list = (wvc_pivot[wvc_pivot.index.isin(word_list)][
                         wvc_pivot['Count'] >= min_count_req].index.values)

        plotter_df = pd.DataFrame()
        for word_main in word_json:
            if word_main not in good_list:
                continue
            other_words = word_json[word_main]
            s = 'Word == "%s"' % (word_main)
            master_df = wcvc_pivot.query(s).reset_index().set_index('Chapter')

            #ensure that all chapters are present for each word
            master_df = master_df.reindex(ch_list).fillna(0)
            master_df['Word'] = word_main

            master_df.sort_index(inplace=True)

            for word_sub in other_words:
                s = 'Word == "%s"' % (word_sub)
                minor_df = wcvc_pivot.query(s).reset_index().set_index('Chapter')
                minor_df = minor_df.reindex(ch_list).fillna(0)
                minor_df.sort_index(inplace=True)
                master_df['Count'] = master_df['Count'] + minor_df['Count']
            plotter_df = pd.concat([plotter_df, master_df])
        plotter_df = plotter_df.reset_index()
        plotter_df.set_index(['Chapter', 'Word'], inplace=True)
        plotter_df = plotter_df.unstack(level=1)
        if max_words == 0:
            plotter_df = plotter_df.drop(plotter_df.sum(axis=0)
                                         [plotter_df.sum(axis=0) <
                                          min_count_req].index, axis=1)
            #sort columns by total word count
            plotter_df = plotter_df[plotter_df.sum(axis=0).sort_values(ascending=False).index]
        else:
            plotter_df = plotter_df[list(plotter_df.sum(axis=0).sort_values(ascending=False)
                                         [-max_words:].index)]
        plotter_df.columns = plotter_df.columns.droplevel(0)
        plotter_df.to_hdf(h5_file, h5_store_name, format='table', append=False)
        return plotter_df

if __name__ == "__main__":
  pass
    # generate_book_df = False
    # generate_toc_df = False
    # book_short_name = 'rafo3r'
    # my_reader = book_reader(book_short_name, generate_book_df, generate_toc_df)

    # book_file = 'rafo3r.txt'
    # h5_file = 'rafo3r.h5'

    # #if running on pythonanywhere
    # #book_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.txt'
    # #h5_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.h5'

    # rafo3r, toc = my_reader.main(book_file, h5_file)

    # now = str(dt.datetime.now())
    # now = now.replace(':', '')
    # now = now.replace(' ', '')
    # now = now.replace('-', '')
    # now = now.replace('.', '')
    # my_reader.csv_dump(rafo3r, 'rafo3r', now)
    # my_reader.csv_dump(toc, 'toc', now)
