from exceptions import DryNoSauceHere, TooManySauce
import img2pdf
import requests
import os


class Pyscandl:
	# TODO: add stand-alone chapter support (replacing if self.fetcher.__class__.__name__ == "NHentai":)
	def __init__(self, fetcher, chapstart:int=1, output:str=".", keepimage:bool=False, all:bool=False, link:str=None, manga:str=None, download_number:int=1, quiet:bool=False, skip:int=0, tiny:bool=False):
		# must have either a link or a manga
		if link is not None and manga is None or link is None and manga is not None:
			self.fetcher = fetcher(link=link, manga=manga, chapstart=chapstart)
		elif link is None and manga is None:
			raise DryNoSauceHere
		else:
			raise TooManySauce
		# creating output folder
		self.output = (output[-1]=="/" and output or output+"/") + self.fetcher.manga_name + "/"
		if not os.path.exists(self.output):
			os.makedirs(self.output)

		self.skip = skip
		self.quiet = quiet
		self.keepimage = keepimage
		self.all = all
		self.download_number = download_number
		self.path = f"{self.output}ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}/"  # save path for images
		self._img_bin_list = []
		self.tiny = tiny

		if self.tiny:
			if self.fetcher.__class__.__name__ == "NHentai":
				self.pdf_path = f"{self.output}{self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"{self.fetcher.chapter_name}"
			else:
				self.pdf_path = f"{self.output}ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"
		else:
			if self.fetcher.__class__.__name__ == "NHentai":
				self.pdf_path = f"{self.output}{self.fetcher.manga_name} - {self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"{self.fetcher.manga_name} - {self.fetcher.chapter_name}"
			else:
				self.pdf_path = f"{self.output}{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"

		self._banlist = []
		ban_path = f"{os.path.dirname(os.path.abspath(__file__))}/banlist"
		for img in os.listdir(ban_path):
			with open(f"{ban_path}/{img}", "rb") as img_bin:
				self._banlist.append(img_bin.read())

	def _ext_check(self):
		img_bin = requests.get(self.fetcher.image).content
		ext = self.fetcher.ext

		if b"404 Not Found" in img_bin:
			if self.fetcher.ext==".jpg":
				img_bin = requests.get(self.fetcher.image.replace(".jpg", ".png").replace(".jpeg", ".png")).content
				ext = ".png"
			else:
				img_bin = requests.get(self.fetcher.image.replace(".png", '.jpg')).content
				ext = ".jpg"
		return img_bin, ext

	def _dl_image(self):
		# single image download
		img_bin, ext = self._ext_check()

		if not os.path.exists(self.path):
			os.makedirs(self.path)

		with open(f"{self.path}{self.fetcher.npage}{ext}", "wb") as img:
			img.write(img_bin)
			if not self.quiet:
				print(".", end="", flush=True)

	def _full_chapter(self):
		# fetching binary data an entire chapter
		if not self.quiet:
			if self.fetcher.__class__.__name__ == "NHentai":
				print(f"fetching: {self.fetcher.chapter_name}")
			else:
				print(f"fetching: ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}")
		while not self.fetcher.is_last_image():
			img_bin, ext = self._ext_check()
			self._img_bin_list.append(img_bin)
			if not self.quiet:
				print(".", end="", flush=True)
			self.fetcher.next_image()
		img_bin, ext = self._ext_check()
		self._img_bin_list.append(img_bin)
		if not self.quiet:
			print(".", end="", flush=True)

	def _keep_full_chapter(self):
		# download a full chapter
		if not self.quiet:
			if self.fetcher.__class__.__name__ == "NHentai":
				print(f"downloading: {self.fetcher.chapter_name}")
			else:
				print(f"downloading: ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}")
		while not self.fetcher.is_last_image():
			self._dl_image()
			self.fetcher.next_image()
		self._dl_image()

	def _skip(self):
		for loop in range(self.skip):
			self.fetcher.next_image()

	def _create_pdf(self):
		print("\nconverting...", end=" ")
		# loading the downloaded images if keep mode
		if self.keepimage:
			for loop in range(1, self.fetcher.npage+1):
				try:
					with open(f"{self.path}{loop}{self.fetcher.ext}", "rb") as img:
						self._img_bin_list.append(img.read())
				except FileNotFoundError:
					ext = self.fetcher.ext==".png" and ".jpg" or ".png"
					with open(f"{self.path}{loop}{ext}", "rb") as img:
						self._img_bin_list.append(img.read())

		# removing the images found in the banlist
		self._img_bin_list = [img for img in self._img_bin_list if img not in self._banlist]

		if len(self._img_bin_list) > 0:
			# creating the pdf
			with open(self.pdf_path, "wb") as pdf:
				pdf.write(img2pdf.convert(self._img_bin_list, title=self.name_metadata_pdf, author=self.fetcher.author, keywords=[self.fetcher.manga_name]))
			print("converted")
		else:
			# creating an empty file to aknowledge the presence of a downed chapter
			with open(f"{self.pdf_path}.empty", "wb"):
				pass
			print("empty")

	def _next_chapter(self):
		# changes to the next chapter and prepare the next image folder
		self.fetcher.next_chapter()
		self.path = f"{self.output}ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}/"
		self._img_bin_list = []
		# prepares the next pdf path and name
		if self.tiny:
			if self.fetcher.__class__.__name__ == "NHentai":
				self.pdf_path = f"{self.output}{self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"{self.fetcher.chapter_name}"
			else:
				self.pdf_path = f"{self.output}ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"
		else:
			if self.fetcher.__class__.__name__ == "NHentai":
				self.pdf_path = f"{self.output}{self.fetcher.manga_name} - {self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"{self.fetcher.manga_name} - {self.fetcher.chapter_name}"
			else:
				self.pdf_path = f"{self.output}{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}.pdf"
				self.name_metadata_pdf = f"{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"

	def full_download(self):
		try:
			# download the full request
			# emulating a do while
			self._skip()
			counter = 1
			if self.keepimage:
				self._keep_full_chapter()
			else:
				self._full_chapter()
			self._create_pdf()
			while not self.fetcher.is_last_chapter() and self.all or counter < self.download_number:
				self._next_chapter()
				if self.keepimage:
					self._keep_full_chapter()
				else:
					self._full_chapter()
				self._create_pdf()
				counter += 1
		except KeyboardInterrupt:
			print("\nmanual interruption")
		finally:
			self.fetcher.quit()
			print("end of the download")
