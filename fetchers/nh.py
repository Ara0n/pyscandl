import exceptions
import requests
import re

#TODO: rework with the class with the api
class Nhentai:
	def __init__(self, link:str=None, manga:int=None, **kwargs):
		# creating the chapter link
		if link is not None:
			self._link = link + (link[-1] == "/" and "1/" or "/1/")
		else:
			self._link = f"https://nhentai.net/g/{manga}/1/"

		# check if exists
		test404 = requests.get(self._link).content
		if b"container error" in test404:
			name = self._link.split("/")[-3]
			raise exceptions.MangaNotFound(name)

		# nhentai has chapters and no manga name so using the tag NSFW as a name
		self.manga_name = "NSFW"

		# getting the source code of the web page
		self._page = requests.get(self._link).content.decode("utf-8").replace("\n", "").replace("\t", "").replace("&#39;", "'")

		# TODO: add self.author
		self.author = "TBD"
		self.npage = 1
		self.chapter_number = 1
		self.ext = ".jpg"

		# finding the chapter name in the title
		self.chapter_name = self._page[self._page.find("<title>")+7:self._page.find("</title>")-53]
		self._last_page = int(re.search(r"<span class=\"num-pages\">(\d{1,3})", self._page).group(1))

		# initializing for the image url
		self._image_root = re.search(r"https://i.nhentai.net/galleries/\d+/", self._page).group()
		self.image = f"{self._image_root}{self.npage}{self.ext}"
		# if the first image is a png switch to it for the default extension
		test_ext = requests.get(self.image)
		if b"404 Not Found" in test_ext.content:
			self.ext = ".png"
			self.image = f"{self._image_root}{self.npage}{self.ext}"

	def next_image(self):
		self.npage += 1
		self.image = self._image_root + str(self.npage) + self.ext

	def next_chapter(self):
		# there is only one chapter for every scan in nhentai
		pass

	def is_last_image(self):
		return self.npage == self._last_page

	def is_last_chapter(self):
		# there is only one chapter for nhentai so it's always true
		return True

	def quit(self):
		# nothing needing a proper closing
		pass
