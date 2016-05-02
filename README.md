# SubScenAPI
A commandline utility / API for the lazy ass to get subtitles from https://subscene.com/.

**SubScenAPI** takes an *IMDB ID* or a *Movie / TV Series* name and gets it's subtitle from https://subscene.com... all from the comfort of your command line. In addition, it supports the following features:

(a) **IMDB ID**
    - *Downloads the movie / TV Series' subtitle if given the IMDB id* (uses `OMDB API` - http://www.omdbapi.com)

(b) **Language Preference**
    - *Get a subtitle in your preferred language*

(c) **Positive-only rated subtitles**
    - *Look for only subtitles that are rated good*.

(d) **Subtitle for Hearing Impaired**
    - *Filter for subtitles that are for exclusively for `hearing impaired`*  

(e) **Tags**
    - *Look for subtitles that matches any/all of those tags. E.g., '1080p', 'YIFY' etc.*


# Requirements
Needs Python 3 and Beautifulsoup.  Do `pip install -r requirements.txt`

# Examples:
1. `$ python3 download_subtitle.py --title Interstellar`  # just the title  (displays a UI if there are multiple matches)
2. `$ python3 download_subtitle.py --id tt0368447`     # IMDB ID
3. `$ python3 download_subtitle.py --lang 'bengali, indonesian' --title 'Rang De Basanti' --tags 'brrip, 720p' `


Enjoy :)
