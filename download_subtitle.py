""" Subscene API (Kind of) to download subtitles """

import argparse
import os
import sys
import re
import urllib.request
from bs4 import BeautifulSoup as bs

user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
hdr = {'User-Agent': user_agent}
subscene_homepage = 'https://subscene.com'

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", help='imdb ID (this or title is mandatory)')
parser.add_argument("-t", "--title", help='movie / TV Series to search for... (this or IMDB-ID is mandatory )')
parser.add_argument("-s", "--silent", action='store_true', help="Silent Mode Silently downloads if there's a perfect \
                                match. No questions asked. Ignores if there are multiple matches - Default : False")
parser.add_argument("-d", "--folder", help='where to save the subtitle. Default (in "~/Downloads/SubScenAPI/")', default=os.path.abspath(os.path.expanduser("~/Downloads/SubScenAPI/")))
parser.add_argument("-l", "--lang", help='Get subtitle only in any of these languages - Default : "english, ")', default='english, ')
parser.add_argument("-x", "--hear", action='store_true', help='Get subtitle for hearing impaired - Default : False')
parser.add_argument("-n", "--top", type=int, help="display top_n results in case there are multiple results (e.g., 'Terminator') - Default: 10", default=10)
parser.add_argument("-r", "--norate", action='store_false', help='get only positively rated subtitle - Default: True')
parser.add_argument("--tags", help="Try to get the subtitle that matches these additional requirements.  E.g., ('720p', 'extended edition') etc. - Default : '1080p, yify' ", default='1080p, yify')
parser.add_argument("-f", "--allTags", action='store_true', help='Force all tags to match - Default: False')

args = parser.parse_args()
if not (args.id or args.title):
    parser.error('Need either IMDB ID or the title to search for.')

class Subscene:

    def __init__(self, imdb_id=None, title=None, silent_download=False, hearing_impaired=False, top_n=10, \
                 download_folder=os.path.expanduser('~/Downloads/SubScenAPI'), tags=['1080p', 'YIFY'], \
                 enforce_all_tags=False, language_preferences=['English'], only_rated=True):
        self.imdb_id = imdb_id
        self.title = title
        self.silent_download = silent_download
        self.download_folder = os.path.abspath(download_folder)
        language_preferences = [ x.strip() for x in language_preferences.split(',')]
        self.language_preferences = [str.lower(lang) for lang in language_preferences]
        self.hearing_impaired = hearing_impaired
        self.only_rated = only_rated
        tags = [ x.strip() for x in tags.split(',')]
        self.tags = [str.lower(tag) for tag in tags]
        self.top_n = top_n
        self.enforce_all_tags = enforce_all_tags

        if not os.path.exists(self.download_folder):
            os.mkdir(self.download_folder)


    def get_title_and_year(self):
        """ Returns the title and year using the 'OMDB' API """

        search_str = 'http://www.omdbapi.com/?i={}'.format(self.imdb_id)
        try:
            omdb_search = urllib.request.urlopen(urllib.request.Request(search_str, headers=hdr), timeout=5)
        except Exception as e:
            print(e)
            sys.exit(-1)

        content = eval(omdb_search.read())
        return content['Title'], content['Year']


    def get_redirection_link(self, search_str, movie_name, year):
        """ Given the search string, returns the final link that matches it the most """

        try:
            website = urllib.request.urlopen(urllib.request.Request(search_str, headers=hdr), timeout=5)
        except Exception as e:
            print (e)
            sys.exit(-1)

        content = website.read()
        soup = bs(content, 'html.parser')

        redirect = None
        # Search results are contained under this tag
        res = soup.findAll("div", { "class" : "search-result" }, recursive=True)[0]

        # If there's an exact match (more than 1 movie possible)
        children = list(res.children)

        # this tag exists only if there's an exact match to the user query
        exact_match = soup.find("h2", { "class" : "exact" }, recursive=True)
        if exact_match is not None:
            # Sometimes, if subscene isn't sure, it puts the 'popular' results on top of 'exact' results
            if 'Exact' in children[1].string:
                exact_matches = children[3]
            else:
                exact_matches = children[7]

            # Get the exact matched results (could be more than one)
            titles = list(exact_matches.stripped_strings)[::2]
            len_titles = len(titles)

            if len_titles > 1:
                # If IMDB ID is specified, then we know the year, so no ambiguity.
                if year:
                    for i in range(len_titles):
                        if '({})'.format(year) in titles[i]:
                            redirect = exact_matches.find_all('a')[i]['href']
                else:

                    # If 'silent_download' mode is ON, then notify the user and exit
                    if self.silent_download:
                        print ('More than 1 exact matching result: {}. \n \
                                Disable "silent_download" & try again. Else give the IMDB id.'.format(titles))
                        sys.exit(0)

                    # UI to select from the matching queries.
                    print ("{} exact matches found... Choose one: ".format(len_titles))
                    for i in range(len(titles)):
                        print ("{}. {}".format(i+1, titles[i]))

                    inp, valid = None, False
                    while not valid:
                        try:
                            inp = int(input('\n Enter id you need the subtitle for... ("-1" to quit): '))
                        except Exception as e:
                            print ('\n Invalid input... Enter just the ID number to the left of any of the title above. ("-1" to quit)')
                            continue

                        if (0 < inp <= len_titles) or (inp == -1):
                            valid = True
                        else:
                            print ('\n Invalid input... Enter just the ID no. to the left of any of the title ("-1" to quit)')

                    if inp == -1:
                        sys.exit(0)

                    redirect = exact_matches.find_all('a')[inp-1]['href']
            else:
                redirect = exact_matches.find_all('a')[0]['href']

        else:
            # If no exact matches, show popular ones if there are any results...
            if 'No results' in str(children[1]):
                print ('No results found... Try again with something else...')
                sys.exit(0)

            if self.silent_download:
                print ('No exact match found... Disable "silent_download" & try again. Else give the IMDB id.')
                sys.exit(0)

            # the 'children' tags are ordered in ['popular', 'matches', 'exact', matches, 'close', matches ]
            # So display them nicely for the user to choose
            # Store the matches in dict to access the correspoding hyperlinks later.
            headers, results = list(range(1, len(children)-3, 4)), list(range(3, len(children)-3, 4))
            search_results = {}

            print ('\n No exact match found...')
            for header, result in zip(headers, results):
                print('\n {}'.format(children[header].string))
                names = list(children[result].stripped_strings)[::2][:self.top_n]
                links = [link.get('href') for link in children[result].find_all('a')[:self.top_n]]
                dc = dict(enumerate(zip(names, links), header*10))
                search_results.update(dc)

                for key in sorted(dc.keys()):
                    print ('{}. {}'.format(key, dc[key][0]))

            valid_inputs = sorted(search_results.keys())
            valid = False
            while not valid:
                try:
                    inp = int(input('\n Enter id you need the subtitle for... ("-1" to quit) : '))
                except Exception as e:
                    print ('\t Invalid input... Enter just the ID number to the left of any of the title above ("-1" to quit)')
                    continue

                if (inp in valid_inputs) or (inp == -1):
                    valid = True
                else:
                    print ('\t Invalid input... Enter just the ID number to the left of any of the title above ("-1" to quit)')

            if inp == -1:
                sys.exit(0)

            redirect = search_results[inp][1]

        return redirect


    def _get_file(self, redirect_link):
        """
            Now that we got the movie / TV series link, download the subtitle that matches the user's preferences
            such as language, tags etc.
        """

        search_str = '{}{}'.format(subscene_homepage, redirect_link)

        try:
            website = urllib.request.urlopen(urllib.request.Request(search_str, headers=hdr), timeout=5)
        except Exception as e:
            print (e)
            sys.exit(-1)

        content = website.read()
        soup = bs(content, 'html.parser')

        table = soup.findChild('tbody')

        # Get only those subtitles that matches the user's language preference
        regex = '|'.join(['(/{}/)'.format(lang) for lang in self.language_preferences])

        # the subtitles with 'hearing_impaired' are under different class
        hearing_class = "a41" if self.hearing_impaired else "a40"

        # Check for unrated subtitle_files as well if the user is OK with it.
        rating = ['positive'] if self.only_rated else ['positive', 'neutral']

        # The conditions are prirotized from high to low in the order : (language, hearing_impaired, rating, tags)
        best_row, better_row, good_row, ok_row = None, None, None, None
        for row in table.find_all('tr'):
            if row.find(href=re.compile(regex)):
                if row.find_all('td', {"class" : hearing_class}):
                    if row.find('span')['class'][-1].split('-')[0] in rating:
                        name = str.lower(list(row.find_all('span')[-1].stripped_strings)[0])
                        if self.enforce_all_tags:
                            if all([x in name for x in self.tags]):
                                best_row = row
                                break
                        elif any([x in name for x in self.tags]):
                            best_row = row
                            break
                        else:
                            better_row = row
                    else:
                        good_row = row
                else:
                    ok_row = row

        best_row = best_row or better_row or good_row or ok_row
        if not best_row:
            print ('No results found that match your criteria. Try modifying/lessening your criteria (tags / lang. preferences)... ')
            sys.exit(0)

        # finally get the subtitle_file's link
        search_str = '{}{}'.format(subscene_homepage, best_row.find('a')['href'])
        try:
            website = urllib.request.urlopen(urllib.request.Request(search_str, headers=hdr), timeout=5)
        except Exception as e:
            print (e)
            sys.exit(-1)

        content = website.read()
        soup = bs(content, 'html.parser')

        # Get the link for the download
        download_link = soup.find('div', {"class":"download"}).find('a')['href']
        download_link = '{}{}'.format(subscene_homepage, download_link)

        try:
            subtitle_file = urllib.request.urlopen(urllib.request.Request(download_link, headers=hdr), timeout=5)
        except Exception as e:
            print (e)
            sys.exit(-1)

        filename = list(best_row.find_all('span')[-1].stripped_strings)[0].strip('.')
        with open(os.path.join(self.download_folder, '{}.zip'.format(filename)), 'wb') as fl:
            fl.write(subtitle_file.read())

        print ('\n\n "{}" saved in "{}"... \n'.format(filename, self.download_folder))


    def download_subtitle(self, imdb_id=None, title=None):
        """ Gets the subtitle file in ZIP file and stores it in the user specified folder """

        assert imdb_id or title, 'Need either IMDB ID or something to search on subscene...'

        year = None
        if imdb_id:
            self.imdb_id = imdb_id
            title, year = self.get_title_and_year()

        self.title = title
        self.title = '+'.join(self.title.split())
        search_str = '{}/subtitles/title?q={}'.format(subscene_homepage, self.title)

        # get the link of the matching query
        redirect_link = self.get_redirection_link(search_str, self.title, year)

        # Download the file
        self._get_file(redirect_link)


if __name__ == '__main__':
    s = Subscene(download_folder=args.folder, silent_download=args.silent, language_preferences=args.lang, \
                 hearing_impaired=args.hear, top_n=args.top, only_rated=args.norate, tags=args.tags, \
                 enforce_all_tags=args.allTags)
    s.download_subtitle(imdb_id=args.id, title=args.title)
