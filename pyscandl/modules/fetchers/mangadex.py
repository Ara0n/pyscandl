from ..excepts import MangaNotFound, EmptyChapter, DelayedRelease
from .fetcher import Fetcher
import cfscrape
import requests
from datetime import datetime


class Mangadex(Fetcher):
	__doc__ = """
	This is the fetcher in charge of https://mangadex.org/ 
	"""

	def __init__(self, link:str=None, manga:str=None, chapstart=1):
		"""
		Initializes the instance of the nhentai fetcher, it needs either manga or link to work.

		:param link: link of the scan wanted
		:type link: str
		:param manga: numbered id corresponding to the manga on the website, ex: 286
		:type manga: str
		:param chapstart: number of the chapter that the download is supposed to start
		:type chapstart: int/float/str

		:raises MangaNotFound: the scan asked for can't be found
		:raises EmptyChapter: the chapter you want to download is empty
		:raises DelayedRelease: the chapter you want to download isn't available yet
		"""

		super().__init__(link, manga, chapstart)
		self.scrapper = cfscrape.create_scraper()

		# getting the manga id
		if link is not None:
			if link[-1] == "/":
				link = link[:-1]
			manga_id = link.split("/")[-2]
		elif manga.isdecimal():
			manga_id = manga
		else:
			# TODO: implement a search function for non id requests
			raise MangaNotFound(manga)

		self.domain = ".mangadex.org"

		manga_json = self.scrapper.get(f"https://mangadex.org/api/manga/{manga_id}").json()
		if manga_json.get("status") == "Manga ID does not exist.":
			raise MangaNotFound(manga_id)

		self._chapters_json = manga_json.get("chapter")

		self._ordered_chaps_json = []
		for item in sorted(self._chapters_json.keys(), key=lambda x: self._chapters_json[x]["chapter"].zfill(10)):
			self._ordered_chaps_json.append((item, self._chapters_json.get(item)))
		self._ordered_chaps_json = [chap for chap in self._ordered_chaps_json if chap[1].get("lang_code")=="gb"]

		self.manga_name = manga_json.get("manga").get("title")
		self.author = manga_json.get("manga").get("author")

		self._chap_id_pos = 0
		while self._chap_id_pos < len(self._ordered_chaps_json) and self._ordered_chaps_json[self._chap_id_pos][1].get("chapter") != str(chapstart):
			self._chap_id_pos += 1
		if self._chap_id_pos >= len(self._ordered_chaps_json):
			raise MangaNotFound(f"{self.manga_name}, chapter {chapstart}")

		self._set_current_chap_info(self._ordered_chaps_json[self._chap_id_pos][0])

	def _set_current_chap_info(self, chap_id):
		"""
		Method used to update the internal info of the parser about the chapter given with the chap_id.

		:param chap_id: id of the chapter we want the info about

		:raises EmptyChapter: the chapter you want to download is empty
		:raises DelayedRelease: the chapter you want to download isn't available yet
		"""

		self.npage = 1
		self._current_chapter_json = self.scrapper.get(f"https://mangadex.org/api/chapter/{chap_id}").json()
		self.chapter_name = self._current_chapter_json.get("title").replace("/", "-")

		self.chapter_number = str(self._current_chapter_json.get("chapter")).split(".")[0].zfill(3)
		if "." in str(self._current_chapter_json.get("chapter")):
			self.chapter_number += "." + str(self._current_chapter_json.get("chapter")).split(".")[1]

		self._img_root = f"{self._current_chapter_json.get('server')}{self._current_chapter_json.get('hash')}/"
		self._img_ids = self._current_chapter_json.get("page_array")

		# checking if chapter is accessible
		if not self._img_ids:
			if self._current_chapter_json.get("status") == "delayed":
				ts = self._current_chapter_json.get("timestamp")
				date = datetime.fromtimestamp(ts)
				raise DelayedRelease(f"{self.manga_name}, chap {self.chapter_number}", date.isoformat(sep=" "))

			raise EmptyChapter(self.manga_name, self.chapter_number)

		self.image = f"{self._img_root}{self._img_ids[0]}"
		self.ext = self._img_ids[0].split(".")[1]

	def next_image(self):
		"""
		Goes to the next image in the scan being fetched.
		"""

		self.image = f"{self._img_root}{self._img_ids[self.npage]}"
		self.ext = self._img_ids[self.npage].split(".")[-1]
		self.npage += 1

	def is_last_image(self):
		"""
		Checks if it's the last image in the current chapter.
		:rtype: bool
		"""

		return self.npage == len(self._img_ids)

	def go_to_chapter(self, chap_num):
		"""
		Make the fetcher go to the asked chapter.

		:param chap_num: chapter number that was asked for
		:type chap_num: int/str/float

		:raises MangaNotFound: the asked chapter doesn't exist
		"""

		self._chap_id_pos = 0
		while self._chap_id_pos < len(self._ordered_chaps_json) and self._ordered_chaps_json[self._chap_id_pos][1].get("chapter") != str(chap_num):
			self._chap_id_pos += 1
		if self._chap_id_pos >= len(self._ordered_chaps_json):
			raise MangaNotFound(f"{self.manga_name}, chapter {chap_num}")

		self._set_current_chap_info(self._ordered_chaps_json[self._chap_id_pos][0])

	def next_chapter(self):
		"""
		Goes to the next chapter
		"""

		self._chap_id_pos += 1
		self._set_current_chap_info(self._ordered_chaps_json[self._chap_id_pos][0])

	def is_last_chapter(self):
		"""
		Checks if the current chapter is the last available one

		:rtype: bool
		"""

		return self._chap_id_pos+1 == len(self._ordered_chaps_json)

	@classmethod
	def scan(cls, link:str=None, manga:str=None):

		header = {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
			"Set-Cookie": "domain=.mangadex.org",
			"Path": "/"
		}

		if link is not None:
			if link[-1] == "/":
				link = link[:-1]
			manga_id = link.split("/")[-2]
		elif manga.isdecimal():
			manga_id = manga
		else:
			raise MangaNotFound(manga)

		manga_json = requests.get(f"https://mangadex.org/api/manga/{manga_id}", headers=header).json()
		if manga_json.get("status") == "Manga ID does not exist.":
			raise MangaNotFound(manga_id)

		if manga_json.get("chapter"):
			chaps = [chap.get("chapter") for chap in manga_json.get("chapter").values() if chap.get("lang_code") == "gb" and chap.get("chapter") != ""]
		else:
			return []

		return list({float(chap) if "." in chap else int(chap) for chap in chaps})

	def quit(self):
		"""
		Method used to close everything that was used after finishing to use the fetcher
		"""

		self.scrapper.close()
