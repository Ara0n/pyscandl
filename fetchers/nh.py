import requests
import re


class Nhentai:
	def __init__(self, link:str=None, manga:str=None):
		# creating the chapter link
		if link is not None:
			self._link = link + (link[-1] == "/" and "1" or "/1/")
		else:
			self._link = "https://nhentai.net/g/" + str(manga) + "/1/"

		# nhentai has chapters and no manga name so using the tag NSFW as a name
		self.manga_name = "NSFW"

		# getting the source code of the web page
		self._page = requests.get(self._link).content.decode("utf-8").replace("\n", "").replace("\t", "").replace("&#39;", "'")

		self._npage = 1
		self.chapter_number = 1

		# finding the chapter name in the title
		self.chapter_name = self._page[self._page.find("<title>") + 7:self._page.find("</title>") - 53]
		self._last_page = int(re.search(r"<span class=\"num-pages\">(\d{1,3})", self._page).group(1))

		# initializing for the image url
		self._image_root = re.search(r"https://i.nhentai.net/galleries/\d+/", self._page).group()
		self.image = self._image_root + str(self._npage) + ".jpg"

	def next_image(self):
		self._npage += 1
		self.image = self._image_root + str(self._npage) + ".jpg"

	def next_chapter(self):
		# there is only one chapter for every scan in nhentai
		pass

	def next(self):
		self.next_image()

	def is_last_image(self):
		return self._page == self._last_page

	@staticmethod
	def is_last_chapter():
		# there is only one chapter for nhentai so it's always true
		return True
