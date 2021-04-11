""" Subscene API (Kind of) to download subtitles """

import argparse
import os
import sys
import re
import urllib.request
import json
from zipfile import ZipFile
import requests
from string import punctuation
from bs4 import BeautifulSoup as bs

user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
hdr = {'User-Agent': user_agent}
subscene_homepage = 'https://subscene.com'

class Subscene:

    def __init__(self, imdb_id=None, title=None, silent_download=False, hearing_impaired=False, top_n=10, \
                 download_folder=os.path.expanduser('~/Downloads/SubScenAPI'), tags=['1080p', 'YIFY'], \
                 enforce_all_tags=False, language_preferences=['English'], only_rated=True):
        self.imdb_id = imdb_id
        self.title = title
        self.silent_download = silent_download
        self.download_folder = os.path.abspath(download_folder)
        self.language_preferences = [str.lower(lang.strip()) for lang in language_preferences]
        self.hearing_impaired = hearing_impaired
        self.only_rated = only_rated
        self.tags = [str.lower(tag.strip()) for tag in tags]
        self.top_n = top_n
        self.enforce_all_tags = enforce_all_tags
        try:
            self.api_key = os.environ['OMDB_API_KEY']
        except KeyError:
            print('please save your OMDB API Key under "OMDB_API_KEY" env var')
            raise
        if not os.path.exists(self.download_folder):
            os.mkdir(self.download_folder)


    def get_title_and_year(self):
        """ Returns the title and year using the 'OMDB' API """

        search_str = 'http://www.omdbapi.com/?i={}&apikey={}'.format(self.imdb_id, self.api_key)
        # assert 0, search_str/
        try:
            resp = requests.post(search_str)
        except Exception as e:
            print(e)
        
        if resp.ok: 
            content = json.loads(resp.content)
            return content['Title'], content['Year']
        else:
            raise ValueError('error fetching data from IMDB')


    def get_redirection_link(self, search_str):
        """ Given the search string, returns the final link that matches it the most """

        try:
            resp = requests.get(search_str)
        except Exception as e:
            print(e)
            sys.exit(-1)

        if not resp.ok:
            raise ValueError('error fetching content')

        soup = bs(resp.content, 'html.parser')
        hrefs = soup.find_all(href=True)
        entries = [x['href'] for x in hrefs if x['href'].startswith('/subtitles')]
        english_entries = [x for x in entries if '/english/' in x]
        resp = requests.get(f'{subscene_homepage}{english_entries[0]}')
        soup = bs(resp.content, 'html.parser')
        download_class = soup.find_all('div', class_='download')[0]
        download_link = download_class.find('a')['href']
        full_download_link = f'{subscene_homepage}{download_link}'
        return full_download_link



    def _get_file(self, redirect_link):
        resp = requests.get(redirect_link)
        if not resp.ok:
            raise ValueError('error fetching data')
        filename = f'{self.title}_subtitles_english.zip'
        with open(filename, 'wb') as fl:
            fl.write(resp.content)
        zip_ref = ZipFile(filename, 'r')
        zip_ref.extractall(filename[:-4])
        zip_ref.close()

        os.remove(filename)
        print(f'downloaded subtitles to "{os.path.abspath(filename[:-4])}" folder')


    def download_subtitle(self, imdb_id=None, title=None):
        """ Gets the subtitle file in ZIP file and stores it in the user specified folder """

        if not (imdb_id or title):
            print ('Need either IMDB ID or something to search on subscene...')
            sys.exit(-1)

        year = None
        if imdb_id:
            # IMDB titles have more prefixed 0s but OMDB API as of now didn't
            # seem to completely understand this... so we change it back temporarily
            # TODO: fix this hack one OMDB API is fixed...
            self.imdb_id = imdb_id.replace('000', '')
            title, year = self.get_title_and_year()

        punc_stripped = title.translate(str.maketrans('', '', punctuation))
        self.title = '-'.join(punc_stripped.split()).lower()
        search_str = '{}/subtitles/{}'.format(subscene_homepage, self.title)

        # get the link of the matching query
        redirect_link = self.get_redirection_link(search_str)

        # Download the file
        self._get_file(redirect_link)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help='imdb ID (this or title is mandatory)')
    parser.add_argument("-t", "--title", help='movie / TV Series to search for... (this or IMDB-ID is mandatory )')
    args = parser.parse_args()
    if not (args.id or args.title):
        parser.error('Need either IMDB ID or the title to search for.')


    s = Subscene()
    s.download_subtitle(imdb_id=args.id, title=args.title)
