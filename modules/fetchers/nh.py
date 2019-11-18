from .. import excepts
import requests


class NHentai:
	def __init__(self, link:str=None, manga:int=None, chapstart=None):
		self.standalone = True
		# chapstart is not used here but needs to be in the definition to respect the fetcher api
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
			raise excepts.MangaNotFound(manga)

		self._corresponding_table = { 'j': "jpg", 'p': "png", 'g': "gif"}
		self.domain = ".nhentai.net"

		# getting the author
		found = False
		i = 0
		while not found:
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
		self.ext = self._corresponding_table.get(self._image_list[self.npage].get('t'))
		self.npage += 1
		self.image = f"{self._image_root}{self.npage}.{self.ext}"

	def next_chapter(self):
		# there is only one chapter for nhentai
		pass

	def is_last_image(self):
		return self.npage == self._manga_json.get("num_pages")

	def is_last_chapter(self):
		# there is only one chapter for nhentai
		return True

	def quit(self):
		# nothing needs to be closed here
		pass
