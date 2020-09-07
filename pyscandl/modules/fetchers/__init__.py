# referencing the fetchers for the PyPI package

from .fanfox import Fanfox

# mangadex setup
from .mangadex import Mangadex
from .mangadex import MangadexEN
from .mangadex import MangadexFR

from .nh import NHentai
from .frscan import FRScan

# naver webtoons
from .naver import NaverWebtoon
from .naver import NaverBestChallenge
from .naver import NaverChallenge

# getting the enumeration
from .fetcher_enum import FetcherEnum
