from ..excepts import MangaNotFound
from .fetcher import StandaloneFetcher
import requests


class NHentai(StandaloneFetcher):
	__doc__ = """
	This is the fetcher in charge of https://nhentai.net/
	The fetcher is of standalone type, it considers every manga as a unique non chaptered scan.
	"""

	def __init__(self, link:str=None, manga:int=None):
		"""
		Initializes the instance of the nhentai fetcher, it needs either manga or link to work.

		:param link: link of the scan wanted
		:type link: str
		:param manga: numbered id corresponding to the manga on the website, ex: 177013
		:type manga: str
		:param chapstart: number of the chapter that the download is supposed to start, it's not used here but needs to be in the definition to respect the fetcher api

		:raises MangaNotFound: the scan asked for can't be found
		"""

		super().__init__(link, manga)
		if link is None:
			self._manga_json = requests.get(f"https://nhentai.net/api/gallery/{manga}").json()
		else:
			if link[-1] == "/":
				manga = link.split("/")[-2]
			else:
				manga = link.split("/")[-1]
			self._manga_json = requests.get(f"https://nhentai.net/api/gallery/{manga}").json()
		# checking if manga exists
		if self._manga_json.get("error"):
			raise MangaNotFound(manga)

		self._corresponding_table = { 'j': "jpg", 'p': "png", 'g': "gif"}
		self.domain = ".nhentai.net"
		self.author = "unknown"

		# getting the author
		found = False
		i = 0
		while not found and i < len(self._manga_json.get("tags")):
			if self._manga_json.get("tags")[i].get("type") == "artist":
				found = True
				self.author = self._manga_json.get("tags")[i].get("name").title()
			else:
				i += 1

		self.npage = 1
		self._image_list = self._manga_json.get("images").get("pages")
		self.ext = self._corresponding_table.get(self._image_list[0].get('t'))
		self._image_root = f"https://i.nhentai.net/galleries/{self._manga_json.get('media_id')}/"
		self.image = f"{self._image_root}{self.npage}.{self.ext}"
		self.manga_name = "NSFW"
		self.chapter_number = 1
		self.chapter_name = f'{self._manga_json.get("title").get("pretty").replace("/", "-")} - {manga}'

	def next_image(self):
		"""
		Goes to the next image in the scan being fetched.
		"""

		self.ext = self._corresponding_table.get(self._image_list[self.npage].get('t'))
		self.npage += 1
		self.image = f"{self._image_root}{self.npage}.{self.ext}"

	def is_last_image(self):
		"""
		Checks if it's the last image in the current chapter
		:rtype: bool
		"""

		return self.npage == self._manga_json.get("num_pages")
