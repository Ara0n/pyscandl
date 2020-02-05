from enum import Enum
from . import nh, fanfox, mangadex
from .. import excepts


class Fetcher(Enum):
	NHENTAI = nh.NHentai
	FANFOX = fanfox.Fanfox
	MANGADEX = mangadex.Mangadex

	@classmethod
	def get(cls, fetcher_name_request: str):
		for i in cls:
			if i.name == fetcher_name_request.upper():
				return i.value
		raise excepts.FetcherNotFound(fetcher_name_request)

	@classmethod
	def list(cls):
		return [i.name for i in cls]
