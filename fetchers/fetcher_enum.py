from enum import Enum
from fetchers import nh, fanfox, fanfox_mono
import exceptions


class Fetcher(Enum):
	# TODO: implement fetchers and add them to this enum
	NHENTAI = nh.Nhentai
	FANFOX = fanfox.Fanfox
	FANFOX_MONO = fanfox_mono.FanfoxMono

	@classmethod
	def get(cls, fetcher_name_request: str):
		for i in cls:
			if i.name == fetcher_name_request.upper():
				return i
		raise exceptions.NoFetcherFound(fetcher_name_request)

	@classmethod
	def list(cls):
		return [i.name for i in cls]
