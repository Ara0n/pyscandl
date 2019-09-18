from enum import Enum
from fetchers import nh, fanfox, fanfox_mono


class Fetcher(Enum):
	# TODO: implement fetchers and add them to this enum
	NHENTAI = nh.Nhentai
	FANFOX = fanfox.Fanfox
	FANFOX_MONO = fanfox_mono.FanfoxMono

	@classmethod
	def get(cls, string: str):
		for i in cls:
			if i.name == string.upper():
				return i

	@classmethod
	def list(cls):
		return [i.name for i in cls]
