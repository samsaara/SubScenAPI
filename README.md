# SubScenAPI
A commandline utility / API for the lazy ass to get subtitles from [SubScene](https://subscene.com/) (https://subscene.com).

**SubScenAPI** takes an *IMDB ID* or a *Movie / TV Series* name and gets it's subtitle from [SubScene](https://subscene.com/)... all from the comfort of your command line. In addition, it supports the following features:

(a) **IMDB ID**
    - *Downloads the movie / TV Series' subtitle if given the IMDB id* (uses [OMDB API](http://www.omdbapi.com))

(b) **Language Preference**
    - *Get a subtitle in your preferred language*

(c) **Positive-only rated subtitles**
    - *Look for only subtitles that are rated good*.

(d) **Subtitle for Hearing Impaired**
    - *Filter for subtitles that are for exclusively for `hearing impaired`*  

(e) **Tags**
    - *Look for subtitles that matches any/all of those tags. E.g., '1080p', 'YIFY' etc.*


# Requirements
Needs Python 3 and [Beautifulsoup](https://www.crummy.com/software/BeautifulSoup/).


Alias it:  `$alias subtitle='python3 download_subtitle.py'` (or something similar)

# Examples:
1. `$ subtitle --title Interstellar`  # just the title  (displays a UI if there are multiple matches)
2. `$ subtitle --id tt0368447`     # IMDB ID
3. `$ subtitle --lang 'bengali, indonesian' --title 'Rang De Basanti' --tags 'brrip, 720p'`

# License
MIT. Read [here](LICENSE.md) for more info.

Enjoy :)
