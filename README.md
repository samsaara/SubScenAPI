# SubScenAPI
A commandline utility / API to get subtitles from https://subscene.com/.

**SubScenAPI** takes an *IMDB ID* or a *Movie / TV Series* name and gets it's subtitle from https://subscene.com... all from the comfort of your command line. In addition, it supports the following features:

(a) **Language Preference**
    - *Get a subtitle in your preferred language*

(b) **Positive-only rated subtitles**
    - *Look for only subtitles that are rated good*.

(c) **Subtitle for Hearing Impaired**
    - *You can filter for subtitles that are for `hearing impaired` *  

(d) **Tags**
    - *Look for subtitles that matches any/all of those tags. E.g., '1080p', 'YIFY' etc.*


# Requirements
Needs Python 3 and Beautifulsoup.  Do `pip install -r requirements.txt`

# Examples:
1. `$ python3 download_subtitle.py --title Interstellar`  # just the title  (displays a UI if there are multiple matches)
2. `$ python3 download_subtitle.py --id tt0368447`     # IMDB ID  (Uses OMDB API for getting movie details - http://www.omdbapi.com/)
3. `$ python3 download_subtitle.py --lang 'bengali, indonesian' --title 'Rang De Basanti' --tags 'brrip, 720p' `


Enjoy :)
