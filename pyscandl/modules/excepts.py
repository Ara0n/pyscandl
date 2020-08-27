class TooManySauce(Exception):
	__doc__ = """
	Exception used if the user has given a link and a manga name at the same time.
	"""

	def __init__(self):
		Exception.__init__(self, "too many sauce, you can't give a manga and a link at the same time")


class DryNoSauceHere(Exception):
	__doc__ = """
	Exception used if the user has given no link or manga
	"""

	def __init__(self):
		Exception.__init__(self, "you need to give either a link to the manga or its name")


class MangaNotFound(Exception):
	__doc__ = """
	Exception used when the asked manga or chapter can't be found
	"""

	def __init__(self, name):
		"""
		:param name: name of the manga
		:type name: str
		"""
		Exception.__init__(self, f"the manga {name} was not found")


class FetcherNotFound(Exception):
	__doc__ = """
	Exception used when the asked fetcher doesn't exists
	"""

	def __init__(self, fetcher):
		"""
		:param fetcher: name of the fetcher
		:type fetcher: str
		"""
		from .fetchers import fetcher_enum  # future proofed for circular imports
		Exception.__init__(self, f"{fetcher.upper()} is not a supported fetcher the list of supported fetchers is: " + ", ".join(
            fetcher_enum.Fetchers.list()))


class NoFetcherGiven(Exception):
	__doc__ = """
	Exception used when there was no fetcher given to the program
	"""

	def __init__(self):
		Exception.__init__(self, "no fetcher given, please give a fetcher")


class IsStandalone(Exception):
	__doc__ = """
	Exception used when trying to add to autodl a scan using a standalone fetcher
	"""

	def __init__(self, name):
		"""
		:param name: name of the manga using the standalone fetcher
		:type name: str
		"""

		Exception.__init__(self, f"{name} has a standalone type fetcher and thus can't be used with autodl")


class EmptyChapter(Exception):
	__doc__ = """
	Exception used when the current chapter is empty
	"""

	def __init__(self, manga, chap_num):
		"""
		:param manga: name of the manga
		:type manga: str
		:param chap_num: chapter number that is empty in :param manga:
		:type chap_num: int/float/str
		"""

		Exception.__init__(self, f"chapter {chap_num} of {manga} is empty")


class DelayedRelease(Exception):
	__doc__ = "exception used if a chapter is visible on the website but will be available later, this can be the case on mangadex"

	def __init__(self, name, date):
		"""
		:param name: name of the manga
		:param date: date of the availability
		"""

		Exception.__init__(self, f'the manga {name} will be available starting {date}')


class DownedSite(Exception):
	__doc__ = """
	Exception used when the fetcher can't access its website to do the downloads
	"""

	def __init__(self, website_name):
		"""
		:param website_name:
		"""

		Exception.__init__(self, f"The website {website_name} isn't accessible for the moment, please retry it later")
