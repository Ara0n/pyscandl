from enum import Enum
from . import NHentai, Fanfox, MangadexEN, MangadexFR, NaverWebtoon, NaverBestChallenge, NaverChallenge, FRScan, WebtoonsEN, WebtoonsFR
from ..excepts import FetcherNotFound


class FetcherEnum(Enum):
	__doc__ = """
	Enumeration of all the fetchers available to the program at the moment
	"""

	NHENTAI = NHentai
	FANFOX = Fanfox
	MANGADEX = MangadexEN
	MANGADEX_FR = MangadexFR
	FRSCAN = FRScan
	NAVERWEBTOON = NaverWebtoon
	NAVERBESTCHALLENGE = NaverBestChallenge
	NAVERCHALLENGE = NaverChallenge
	WEBTOONS = WebtoonsEN
	WEBTOONS_FR = WebtoonsFR

	@classmethod
	def get(cls, fetcher_name_request: str):
		"""
		Class method used to  get the corresponding fetcher that was asked for

		:param fetcher_name_request: name of the asked fetcher
		:type fetcher_name_request: str

		:return: corresponding fetcher object

		:raises FetcherNotFound: the name given doesn't correspond to one of the available fetchers
		"""

		for i in cls:
			if i.name == fetcher_name_request.upper():
				return i.value
		raise FetcherNotFound(fetcher_name_request)

	@classmethod
	def list(cls):
		"""
		Gives a list of all the available fetchers at the moment.
		:rtype: list[str]
		"""
		return [i.name for i in cls]
