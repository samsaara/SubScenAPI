import os
from shutil import rmtree
import pytest
from json.decoder import JSONDecodeError
from subscenapi.subtitle import Subscene

def test_subtitle_valid_imdb_id():
    s = Subscene()
    invalid_id = 'tt036844734'
    with pytest.raises(KeyError):
        s.download_subtitle(imdb_id=invalid_id)


def test_downloaded_subtitle():
    s = Subscene()
    valid_imdb_id = 'tt0368447'
    s.download_subtitle(imdb_id=valid_imdb_id)
    filepath = 'data/the-village_subtitles_english'
    assert os.path.exists(filepath)

    # cleanup
    rmtree(filepath)

