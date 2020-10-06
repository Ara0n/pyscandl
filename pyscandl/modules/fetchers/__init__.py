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

# webtoons setup
from .webtoons import Webtoons
from .webtoons import WebtoonsEN
from .webtoons import WebtoonsFR

# getting the enumeration
from .fetcher_enum import FetcherEnum
