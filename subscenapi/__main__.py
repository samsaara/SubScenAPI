import argparse
from subtitle import Subscene


def get_subtitle(id=None, title=None):
    s = Subscene()
    s.download_subtitle(imdb_id=id, title=title)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help='imdb ID (this or title is mandatory)')
    parser.add_argument("-t", "--title", help='movie / TV Series to search for... (this or IMDB-ID is mandatory )')
    args = parser.parse_args()
    if not (args.id or args.title):
        parser.error('Need either IMDB ID or the title to search for.')
    get_subtitle(args.id, args.title)
