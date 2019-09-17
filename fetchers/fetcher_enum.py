from enum import Enum
from fetchers import nh, fanfox


class Fetcher(Enum):
	# TODO: implement fetchers and add them to this enum
	NHENTAI = nh.Nhentai
	FANFOX = fanfox.Fanfox

	@classmethod
	def get(cls, string: str):
		for i in cls:
			if i.name == string.upper():
				return i

	@classmethod
	def list(cls):
		return [i.name for i in cls]
