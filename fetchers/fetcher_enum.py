from enum import Enum
from fetchers import nh


class fetcher(Enum):
	# TODO: implement fetchers and add them to this enum
	NHENTAI = nh.Nhentai

	@classmethod
	def get(cls, string: str):
		for i in cls:
			if i.name == string.upper():
				return i

	@classmethod
	def list(cls):
		return [i.name for i in cls]
