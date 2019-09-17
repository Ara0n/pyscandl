from selenium import webdriver
from selenium.common import exceptions
import re


class Fanfox:
	def __init__(self, link:str=None, manga:str=None, chapstart:int=1):
		# creating the chapter link
		if link is not None:
			self._link = link + (link[-1] == "/" and "" or "/")
			self.manga_name = self._link.split("/")[-2].replace("_", " ").title()
		else:
			self._link = f"https://fanfox.net/manga/{manga.replace(' ', '_').lower()}/"
			self.manga_name = manga.replace("_", " ").title()

		option = webdriver.FirefoxOptions()
		option.headless = False
		self.driver = webdriver.Firefox(options=option)

		self.urlpage = f"{self._link}c{str(chapstart).zfill(3)}/1.html"
		self.driver.get(self.urlpage)
		self.npage = 1
		self.chapter_number = chapstart
		self.ext = ".jpg"

		self._last_page = self.driver.find_element_by_css_selector(".pager-list-left span a:last-child").text
		if self._last_page == ">":
			self._last_page = self.driver.find_element_by_css_selector(".pager-list-left span a:nth-last-child(2)").text
		self._last_page = int(self._last_page)

		self.image =  self.driver.find_element_by_class_name("reader-main-img").get_attribute("src").split("?")[0]

		temp_title = self.driver.find_element_by_class_name("reader-header-title-2").text
		self.chapter_name = re.search(r"(?:Vol\.\d{2} Ch\.\d{3}(\.\d)? )(.*)", temp_title).group(2)
		if self.chapter_name is None:
			self.chapter_name = ""

	def next_image(self):
		self.npage += 1
		self.driver.find_element_by_css_selector(".pager-list-left span a:last-child").click()
		while "https://static.fanfox.net/v201906282/mangafox/images/loading.gif" in self.driver.find_element_by_class_name("reader-main-img").get_attribute("src"):
			pass
		self.image = self.driver.find_element_by_class_name("reader-main-img").get_attribute("src").split("?")[0]

	def next_chapter(self):
		self.chapter_number += 1
		self.chapter_name = self.driver.find_element_by_css_selector(".pager-list-left span a:nth-last-child(2)").get_attribute("title")
		self.npage = 1
		self.driver.find_element_by_css_selector(".pager-list-left .chapter:last-child").click()

		self._last_page = self.driver.find_element_by_css_selector(".pager-list-left span a:last-child").text
		if self._last_page == ">":
			self._last_page = int(self.driver.find_element_by_css_selector(".pager-list-left span a:nth-last-child(2)").text)

	def is_last_image(self):
		return self.npage == self._last_page

	def is_last_chapter(self):
		return self.driver.find_element_by_css_selector(".pager-list-left .chapter:last-child").text != "Next Chapter"

	def quit(self):
		self.driver.quit()