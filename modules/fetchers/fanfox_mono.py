from .. import excepts
from selenium import webdriver
from selenium.common import exceptions
import re
import os


class FanfoxMono:
	def __init__(self, link:str=None, manga:str=None, chapstart:int=1):
		self.standalone = False
		# creating the chapter link
		if link is not None:
			if link[-1] == "/":
				self._link = link
			else:
				self._link = link + "/"
			self.manga_name = self._link.split("/")[-2].replace("_", " ").title()
		else:
			self._link = f"https://fanfox.net/manga/{manga.replace(' ', '_').lower()}/"
			self.manga_name = manga.replace("_", " ").title()

		option = webdriver.FirefoxOptions()
		option.headless = True
		self.driver = webdriver.Firefox(options=option)
		self.domain = ".fanfox.net"

		# getting the author and checking if manga exists
		self.driver.get(self._link)
		if self.driver.current_url != self._link:
			self.quit()
			raise excepts.MangaNotFound(self.manga_name)
		self.author = self.driver.find_element_by_class_name("detail-info-right-say").find_element_by_css_selector("a").text

		temp_num = str(chapstart).split(".")[0].zfill(3)
		if "." in str(chapstart):
			temp_num += "." + str(chapstart).split(".")[1]
		self.urlpage = f"{self._link}c{temp_num}/1.html"
		self.driver.get(self.urlpage)

		# checking if chapter exists
		if self.driver.title == "404":
			self.quit()
			raise excepts.MangaNotFound(f"{self.manga_name}, chapter {temp_num}")

		# do the adult check if needed
		try:
			self.driver.find_element_by_id("checkAdult").click()
		except exceptions.NoSuchElementException:
			pass

		self.npage = 1
		self.chapter_number = temp_num
		self._re_chapnum = re.compile(r"^(?:Vol\.(?:\d+|TBD) )?Ch\.(\d+(\.\d+)?)")

		self._img_list = []
		self._last_page = 0
		self.image = ""
		self._refresh_images()
		self.ext = self.image.split(".")[-1]

		temp_title = self.driver.find_element_by_class_name("reader-header-title-2").text
		self.chapter_name = re.search(r"(?:(Vol\.\d{2} )?Ch\.\d{3}(\.\d)?\s?((- )?(Vol.\d+ )?(Ch.\d+:? ))?)(.*)", temp_title).group(7)
		if self.chapter_name is None:
			self.chapter_name = ""

	def _refresh_images(self):
		self._img_list.clear()
		temp_img_list = self.driver.find_elements_by_class_name("reader-main-img")
		for i in temp_img_list:
			self._img_list.append(f"https:{i.get_attribute('data-src').split('?')[0]}")
		self.image = self._img_list[0]
		self._last_page = len(self._img_list)

	def next_image(self):
		self.image = self._img_list[self.npage]
		self.ext = self.image.split(".")[-1]
		self.npage += 1

	def next_chapter(self):
		chap_name = self.driver.find_element_by_css_selector(".pager-list-left .chapter:last-child")
		self.chapter_name = chap_name.get_attribute("title")
		self.npage = 1
		chap_name.click()
		self._refresh_images()

		temp_name = self.driver.find_element_by_class_name("reader-header-title-2").text
		self.chapter_number = self._re_chapnum.match(temp_name).group(1)

	def is_last_image(self):
		return self.npage == self._last_page

	def is_last_chapter(self):
		try:
			return self.driver.find_element_by_css_selector(".pager-list-left .chapter:last-child").text != "Next Chapter"
		except exceptions.NoSuchElementException:
			return True

	def quit(self):
		self.driver.quit()
		# removing the logs of selenium
		try:
			os.remove("geckodriver.log")
		except FileNotFoundError:
			pass