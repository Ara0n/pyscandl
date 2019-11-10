from .. import excepts
import cfscrape


class Mangadex:
	def __init__(self, link:str=None, manga:str=None, chapstart:int=1):
		self.scrapper = cfscrape.create_scraper()
		self.standalone = False

		# getting the manga id
		if link is not None:
			if link[-1] == "/":
				link = link[:-1]
			manga_id = link.split("/")[-2]
		elif manga.isdecimal():
			manga_id = manga
		else:
			#TODO: implement a search function for non id requests
			raise excepts.MangaNotFound(manga)

		self.domain = ".mangadex.org"

		manga_json = self.scrapper.get(f"https://mangadex.org/api/manga/{manga_id}").json()
		if manga_json.get("status") == "Manga ID does not exist.":
			raise excepts.MangaNotFound(manga_id)

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
			raise excepts.MangaNotFound(f"{self.manga_name}, chapter {chapstart}")

		self._set_current_chap_info(self._ordered_chaps_json[self._chap_id_pos][0])

	def _set_current_chap_info(self, chap_id):
		self.npage = 1
		self._current_chapter_json = self.scrapper.get(f"https://mangadex.org/api/chapter/{chap_id}").json()
		self.chapter_name = self._current_chapter_json.get("title")

		self.chapter_number = str(self._current_chapter_json.get("chapter")).split(".")[0].zfill(3)
		if "." in str(self._current_chapter_json.get("chapter")):
			self.chapter_number += "." + str(self._current_chapter_json.get("chapter")).split(".")[1]

		self._img_root = f"{self._current_chapter_json.get('server')}{self._current_chapter_json.get('hash')}/"
		self._img_ids = self._current_chapter_json.get("page_array")
		self.image = f"{self._img_root}{self._img_ids[0]}"
		self.ext = self._img_ids[0].split(".")[1]

	def next_image(self):
		self.image = f"{self._img_root}{self._img_ids[self.npage]}"
		self.ext = self._img_ids[self.npage].split(".")[-1]
		self.npage += 1

	def is_last_image(self):
		return self.npage == len(self._img_ids)

	def go_to_chapter(self, chap_num):
		self._chap_id_pos = 0
		while self._chap_id_pos < len(self._ordered_chaps_json) and self._ordered_chaps_json[self._chap_id_pos][1].get("chapter") != str(chap_num):
			self._chap_id_pos += 1
		if self._chap_id_pos >= len(self._ordered_chaps_json):
			raise excepts.MangaNotFound(f"{self.manga_name}, chapter {chap_num}")

		self._set_current_chap_info(self._ordered_chaps_json[self._chap_id_pos][0])

	def next_chapter(self):
		self._chap_id_pos += 1
		self._set_current_chap_info(self._ordered_chaps_json[self._chap_id_pos][0])

	def is_last_chapter(self):
		return self._chap_id_pos+1 == len(self._ordered_chaps_json)

	def quit(self):
		self.scrapper.close()
