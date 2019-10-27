from enum import Enum
from fetchers import nh, fanfox, fanfox_mono, mangadex
import excepts


class Fetcher(Enum):
	NHENTAI = nh.NHentai
	FANFOX = fanfox.Fanfox
	FANFOX_MONO = fanfox_mono.FanfoxMono
	MANGADEX = mangadex.Mangadex

	@classmethod
	def get(cls, fetcher_name_request: str):
		for i in cls:
			if i.name == fetcher_name_request.upper():
				return i
		raise excepts.NoFetcherFound(fetcher_name_request)

	@classmethod
	def list(cls):
		return [i.name for i in cls]
