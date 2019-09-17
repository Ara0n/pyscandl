import requests
import os
import shutil
import subprocess


class Pyscandl:
	def __init__(self, fetcher, chapstart:int=1, output:str=".", keepimage:bool=False, all:bool=False, link:str=None, manga:str=None, download_number:int=1, quiet:bool=False):
		# must have either a link or a manga
		if link is not None and manga is None or link is None and manga is not None:
			self.fetcher = fetcher(link=link, manga=manga, chapstart=chapstart)
		else:
			# TODO: make custom exception one day to implement them here
			pass

		self.quiet = quiet
		self.output = (output[-1]=="/" and output or output+"/") + self.fetcher.manga_name + "/"
		self.keepimage = keepimage
		self.all = all
		self.download_number = download_number
		self.path = f"{self.output}{self.fetcher.chapter_name} ch.{self.fetcher.chapter_number}/"  # save path for images

	def _dl_image(self):
		# single image download
		img_bin = requests.get(self.fetcher.image).content

		if not os.path.exists(self.path):
			os.makedirs(self.path)

		with open(f"{self.path}{self.fetcher.npage}{self.fetcher.ext}", "wb") as img:
			img.write(img_bin)
			if not self.quiet:
				print(".", end="", flush=True)

	def _full_chapter(self):
		# download a full chapter
		if not self.quiet:
			print(f"downloading: ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}")
		while not self.fetcher.is_last_image():
			self._dl_image()
			self.fetcher.next_image()
		self._dl_image()


	def _to_pdf(self):
		# create the pdf and delete the images if needed
		print("\nconverting...", end=" ")
		subprocess.run(f"convert \"{self.path}%d{self.fetcher.ext}[1-{self.fetcher.npage}]\" \"{self.output}{self.fetcher.manga_name} - {self.fetcher.chapter_name} ch.{self.fetcher.chapter_number}.pdf\"",
					   shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		if not self.keepimage:
			shutil.rmtree(self.path)
		print("converted")

	def _next_chapter(self):
		# changes to the next chapter and prepare the next image folder
		self.fetcher.next_chapter()
		self.path = f"{self.output}{self.fetcher.chapter_name} ch.{self.fetcher.chapter_number}/"

	def full_download(self):
		# download the full request
		# emulating a do while
		counter = 1
		self._full_chapter()
		self._to_pdf()
		while not self.fetcher.is_last_chapter() and self.all or counter < self.download_number:
			self._next_chapter()
			self._full_chapter()
			self._to_pdf()
			counter += 1
		self.fetcher.quit()
		print("end of the download")

		# removing the logs of selenium
		try:
			os.remove("geckodriver.log")
		except FileNotFoundError:
			pass
