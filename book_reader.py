# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import re
import datetime as dt

class book_reader():
    
    def __init__(self, book_short_name, generate_book_df = False, generate_toc_df = False, generate_pivots = False):
        self.generate_book_df = generate_book_df
        self.generate_toc_df = generate_toc_df
        self.generate_pivots = generate_pivots
        self.re_splitter = r'[;,.?†‡!"”()\]\[\*:\s\n]\s*'
        self.book_short_name = book_short_name
		
        #Stopwords from http://www.lextek.com/manuals/onix/stopwords1.html
        self.stopwords = ['a', ' about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost',
               'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and',
               'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas',
               'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away', 'b', 'back', 'backed',
               'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before',
               'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but',
               'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear',
               'clearly', 'come', 'could', 'd', 'did', 'differ', 'different', 'differently', 'do',
               'does', 'done', 'down', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each',
               'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly', 'ever',
               'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact',
               'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full',
               'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally',
               'get', 'gets', 'give', 'given', 'gives', 'go', 'going', 'good', 'goods', 'got', 'great',
               'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have',
               'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him',
               'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested',
               'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep',
               'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later',
               'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm',
               'made', 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might',
               'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary',
               'need', 'needed', 'needing', 'needs', 'never', 'new', 'new', 'newer', 'newest', 'next',
               'no', 'nobody', 'non', 'noone', 'not', 'nothing', 'now', 'nowhere', 'number', 'numbers',
               'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once', 'one', 'only', 'open',
               'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other',
               'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps',
               'place', 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented',
               'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather',
               'really', 'right', 'right', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second',
               'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she',
               'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'small', 'smaller',
               'smallest', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'state', 'states',
               'still', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that', 'the', 'their', 'them',
               'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this',
               'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together',
               'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until',
               'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting',
               'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where',
               'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without',
               'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'year', 'years', 'yet', 'you', 'young',
               'younger', 'youngest', 'your', 'yours', 'z']
        #my additions
        self.stopwords += ['', '-', '–','‡','†']
        
    def main(self, book_file, h5_file): 
        print ('Starting')
        h5store = pd.HDFStore(h5_file)
        if self.generate_book_df:
            book_df = self.process_book(book_file, h5_file)
        else:
            book_df = pd.read_hdf(h5_file, self.book_short_name)
        print ('Book processed')
        if self.generate_toc_df:
            toc = self.process_toc(book_df, h5_file)
        else:
            toc = pd.read_hdf(h5_file, 'toc')   
        print ('TOC processed')
        if self.generate_book_df or self.generate_toc_df: #if either one
            book_df = self.chapter_marker(h5_file)
        print ('Chapter Markers made')
        if self.generate_pivots:
            p1, p2 = self.make_pivots(h5_file)
        else:
            p1 = pd.read_hdf(h5_file, self.book_short_name+'_pivot1')
            p2 = pd.read_hdf(h5_file, self.book_short_name+'_pivot2')
        print ('Pivots processed')        
        h5store.close()

        return book_df, toc, p1, p2
    
    def de_possessive(self,word):
        if word.endswith("'s") or word.endswith("’s"):
            word = word[:-2]
        elif word.endswith("'") or word.endswith("’"):
            word = word[:-1]
        return word
    
    def de_quote(self,word):
        if word.startswith('"') or word.startswith('”') or word.startswith("'") or word.startswith("’"):
            word = word[1:]
        if word.endswith('"') or word.endswith('”') or word.endswith("'") or word.endswith("’"):
            word = word[:-1]
        return word
    
    def is_stop_word(self,word):
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
    
        book_list = list(filter(None, book_list)) # remove empty strings
        book_list = list(map(lambda s:s.lower(), book_list))
        book_list = list(map(self.de_quote,book_list))
        book_list = list(map(self.de_possessive,book_list))
    
        book_df = pd.DataFrame(book_list)
        book_df.rename(columns={0: 'Word'}, inplace=True)
        book_df['Stop Word'] = book_df['Word'].apply(self.is_stop_word)
        count = book_df['Word'][book_df['Stop Word'] == False].value_counts(sort=True)
        
        book_df['Count'] = 0
        book_df['Running Count'] = 0
        for w, c in count.iteritems():
            book_df.loc[book_df['Word'] == w,'Count'] = c
            book_df.loc[book_df['Word'] == w,'Running Count'] = list(range(1,c+1))
        book_df['Position'] = book_df.index

        book_df.to_hdf(h5_file,self.book_short_name,format='table',append=False)
        
        #simpler way
        #occurances = rafo3r.groupby('Word').size()
        #mega_words = occurances.index[occurances >= 1000]
        #rafo3r.index = rafo3r['Word']
        
        return book_df
    
    def process_toc(self, book_df, h5_file):
        maj_section_nums = ['One', 'Two', 'Three', 'Four', 'Five', 'Six']
        books = []
        for b in maj_section_nums:
            books.append('Book %s:'%(b))
        
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
                phrase = ['book', maj_section_nums[int(section_id[1:]) - 1].lower()]

            section_title = ' '.join(section_title_split)
            section_title = ' '.join(phrase) + ' ' + section_title

            book_row = next(book_df_iterator)
            book_row_index = book_row[0]
            
            if book_row_index >= (len(book_df) - len(phrase) - len(section_title_split) + 1): break
            
            test_string = None
            while test_string != section_title: 
                test_string_list = []
                for i in range(len(section_title_split) + len(phrase)):
                    if book_row_index + i < len(book_df):
                        test_string_list.append(book_df.at[book_row_index + i, 'Word'])
                test_string = ' '.join(test_string_list)
                try:
                    book_row = next(book_df_iterator)
                    book_row_index = book_row[0]
                except StopIteration:
                    #you have reached the end of the book, but you havent matched
                    #all of the sections. 
                    #restart at the top of the book and move to the next section
                    print ('Error. No matches found for %s'%section_id)
                    book_df_iterator = book_df.iterrows() #reset to top of book
                    break # move to the next toc_row
                
            else:
                #found the match for this section start
                toc.at[section_id,'Location'] = book_row_index - 1  
        
        toc.to_hdf(h5_file,'toc',format='table',append=False)
        
        return toc
        
    def chapter_marker(self, h5_file):
        book_df = pd.read_hdf(h5_file, self.book_short_name)
        toc = pd.read_hdf(h5_file, 'toc')
        toc_books = toc[toc.index.str.startswith("B")]
        toc_chapters = toc[toc.index.str.startswith("Ch")]
        book_df['Book'] = np.searchsorted(toc_books['Location'], book_df['Position']) + 1
        book_df['Chapter'] = np.searchsorted(toc_chapters['Location'], book_df['Position']) + 1
        book_df.to_hdf(h5_file,self.book_short_name,format='table',append=False)
        return book_df
        
    def make_pivots(self,h5_file):
        book_df = pd.read_hdf(h5_file, self.book_short_name)
        def _start_loc(x):
            return int(100 * min(x) / len(book_df))
        def _end_loc(x):
            return int(100 * max(x) / len(book_df))
        book_df_pt = book_df[book_df['Stop Word'] == False].pivot_table(values='Position', 
                    aggfunc=[len,_start_loc,_end_loc], index='Word')
        book_df_pt.sort_values('len',ascending=False,inplace=True)
        book_df_pt.rename(columns={'len': 'Count'}, inplace=True)
        
        book_df_pt2 = book_df[book_df['Stop Word'] == False].pivot_table(values='Position', 
                     aggfunc=[len], index=['Word','Book','Chapter'])
        book_df_pt2.sort_values('len',ascending=False,inplace=True)
        book_df_pt2.rename(columns={'len': 'Count'}, inplace=True)

        book_df_pt.to_hdf(h5_file,self.book_short_name + '_pivot1',format='table',append=False)
        book_df_pt2.to_hdf(h5_file,self.book_short_name + '_pivot2',format='table',append=False)
        #TODO: There is a bug in this file that needs to be fixed. Around row 79117 there is a dupe
        #of h*tler for ch. 1. THere can only be 1 of a word/chapter pair. 
        return book_df_pt, book_df_pt2     
    
if __name__ == "__main__":
    generate_book_df = False
    generate_toc_df = False
    book_short_name = 'rafo3r'
    my_reader = book_reader(book_short_name, generate_book_df, generate_toc_df)

    book_file = 'rafo3r.txt'
    h5_file = 'rafo3r.h5'
    
    #if running on pythonanywhere
    #book_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.txt'
    #h5_file = os.getcwd() + os.sep + 'rafo3r' + os.sep + 'rafo3r.h5'    
    
    rafo3r, toc = my_reader.main(book_file, h5_file)
    
    now = str(dt.datetime.now())
    now = now.replace(':','')
    now = now.replace(' ','')
    now = now.replace('-','')
    now = now.replace('.','')
    my_reader.csv_dump(rafo3r,'rafo3r',now)
    my_reader.csv_dump(toc,'toc',now)
    
    