from .fetchers import fetcher_enum


class TooManySauce(Exception):
	def __init__(self):
		Exception.__init__(self, "too many sauce, you can't give a manga and a link at the same time")


class DryNoSauceHere(Exception):
	def __init__(self, manual=True, rss=False):
		if manual:
			Exception.__init__(self, "you need to give either a link to the manga or its name")
		elif rss:
			Exception.__init__(self, "you need to give a link to rss of the manga")
		else:
			Exception.__init__(self, "you need to give a link to the manga")


class MangaNotFound(Exception):
	def __init__(self, name):
		Exception.__init__(self, f"the manga {name} was not found")


class NoFetcherFound(Exception):
	def __init__(self, fetcher):
		Exception.__init__(self, f"{fetcher.upper()} is not a supported fetcher the list of supported fetchers is: " + ", ".join(fetcher_enum.Fetcher.list()))


class NoFetcherGiven(Exception):
	def __init__(self):
		Exception.__init__(self, "no fetcher given, please give a fetcher")


class IsStandalone(Exception):
	def __init__(self, name):
		Exception.__init__(self, f"{name} has a standalone type fetcher and thus can't be used with autodl")
