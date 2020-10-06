from .excepts import DryNoSauceHere, TooManySauce, EmptyChapter, DelayedRelease
from .fetchers.fetcher import StandaloneFetcher
from PIL import Image
import img2pdf
import requests
import logging
import os
import io
from re import sub as re_sub


class Pyscandl:
	"""
	The main object of the program. It is responsible of the downloads and controls the fetchers for you.
	"""
	def __init__(self, fetcher, chapstart=1, output:str=".", pdf:bool=True, keep:bool=False, image:bool=False, all:bool=False, link:str=None, manga:str=None, download_number:int=1, chapend=0, quiet:bool=False, skip:int=0, tiny:bool=False):
		"""
		Initialize this instance of the pyscandl downloader, it needs either manga or link to work.

		:param fetcher: fetcher object related to the download
		:param chapstart: first chapter to be downloaded
		:type chapstart: int/float/str
		:param output: output folder
		:type output: str
		:param pdf: tell if the result should be kept as a pdf
		:type pdf: bool
		:param keep: tell if the result should be kept as a pdf and as a collection of images
		:type keep: bool
		:param image: tell if the result should be kept as a collection of images
		:type image: bool
		:param all: download all the chapters that are available after chapstart
		:type all: bool
		:param link: link of the manga to download
		:type link: str
		:param manga: identification tag of the manga *(see every fetcher for their different variations)*
		:type manga: str
		:param download_number: number of chapters to download
		:type download_number: int
		:param chapend: chapter to end the download on, if non exstant the download will stop once the next to download chapter number is greater than it
		:type chapend: int/float/str
		:param quiet: should the program not output any information about what it is doing in the console
		:type quiet: bool
		:param skip: number of images to skip on the first chapter being downloaded *(useful if running in image mode)*
		:type skip: int
		:param tiny: should the name of every downloaded scan be minified and only include the chapter number and the chapter title
		:type tiny: bool

		:raises DryNoSauceHere: neither link or manga was specified
		:raises TooManySauce: both link and manga were specified
		"""

		if link is not None and manga is None or link is None and manga is not None:
			if issubclass(fetcher, StandaloneFetcher):
				self.fetcher = fetcher(link=link, manga=manga)
			else:
				self.fetcher = fetcher(link=link, manga=manga, chapstart=chapstart)
		elif link is None and manga is None:
			raise DryNoSauceHere
		else:
			raise TooManySauce

		# in case windows is the os, remove the banned characters
		if os.name == "nt":
			manga_name = re_sub(r'[\\/*?:"<>|]', u"█", self.fetcher.manga_name)
		else:
			manga_name = self.fetcher.manga_name

		# creating output folder
		self._output = (output[-1] == "/" and output or output + "/") + manga_name + "/"

		if not os.path.exists(self._output):
			os.makedirs(self._output)

		self._header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
					   "Set-Cookie": f"domain={self.fetcher.domain}"}
		self._header.update(self.fetcher.headers)
		self._nskip = skip
		self._quiet = quiet

		# select download mode
		self._pdf = pdf
		self._keep = keep
		self._image = image

		self._all = all
		self._download_number = download_number
		self._chapend = chapend
		self._path = f"{self._output}ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}/"  # save path for images
		self._img_bin_list = []
		self._tiny = tiny

		# in case windows is the os, remove the banned characters
		if os.name == "nt":
			chapter_name = re_sub(r'[\\/*?:"<>|]', u"█", self.fetcher.chapter_name)
		else:
			chapter_name = self.fetcher.chapter_name

		if self._tiny:
			if isinstance(self.fetcher, StandaloneFetcher):
				self._pdf_path = f"{self._output}{chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.chapter_name}"
			else:
				self._pdf_path = f"{self._output}ch.{self.fetcher.chapter_number} {chapter_name}.pdf"
				self._name_metadata_pdf = f"ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"
		else:
			if isinstance(self.fetcher, StandaloneFetcher):
				self._pdf_path = f"{self._output}{manga_name} - {chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.manga_name} - {self.fetcher.chapter_name}"
			else:
				self._pdf_path = f"{self._output}{manga_name} - ch.{self.fetcher.chapter_number} {chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"

		self._banlist = []
		ban_path = f"{os.path.dirname(os.path.abspath(__file__))}/../banlist"
		for img in os.listdir(ban_path):
			with open(f"{ban_path}/{img}", "rb") as img_bin:
				self._banlist.append(img_bin.read())

		# disabling logging for alpha-channels for img2pdf
		logging.disable()

	def _dl_image(self):
		"""
		Downloads the currently selected image.
		"""

		if not os.path.exists(self._path):
			os.makedirs(self._path)

		with open(f"{self._path}{self.fetcher.npage}.{self.fetcher.ext}", "wb") as img:
			img.write(requests.get(self.fetcher.image, headers=self._header).content)
			if not self._quiet:
				print(".", end="", flush=True)

	def full_chapter(self):
		"""
		Fetching all the images of the chapter and storing them in RAM.
		"""

		if not self._quiet:
			if isinstance(self.fetcher, StandaloneFetcher):
				print(f"fetching: {self.fetcher.chapter_name}")
			else:
				print(f"fetching: ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}")
		while not self.fetcher.is_last_image():
			self._img_bin_list.append(requests.get(self.fetcher.image, headers=self._header).content)
			if not self._quiet:
				print(".", end="", flush=True)
			self.fetcher.next_image()
		self._img_bin_list.append(requests.get(self.fetcher.image, headers=self._header).content)
		if not self._quiet:
			print(".", end="", flush=True)

	def keep_full_chapter(self):
		"""
		Downloading all the images of the chapters and storing them where the output was specified.
		"""

		if not self._quiet:
			if isinstance(self.fetcher, StandaloneFetcher):
				print(f"downloading: {self.fetcher.chapter_name}")
			else:
				print(f"downloading: ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}")
		while not self.fetcher.is_last_image():
			self._dl_image()
			self.fetcher.next_image()
		self._dl_image()
		if not self._quiet and self._image:
			print("")

	def _skip(self):
		"""
		Skips the images as asked with the skip parameter.
		"""

		for loop in range(self._nskip):
			self.fetcher.next_image()

	def create_pdf(self):
		"""
		Creates the pdf at the output location with the fetched or the downloaded images of the current chapter.

		:raises EmptyChapter: the images of the current chapter were all blacklisted images and the pdf was empty
		"""
		if not self._quiet:
			print("\nconverting...", end=" ")
		# loading the downloaded images if keep mode
		if self._keep:
			for loop in range(1, self.fetcher.npage + 1):
				try:
					with open(f"{self._path}{loop}.jpg", "rb") as img:
						self._img_bin_list.append(img.read())
				except FileNotFoundError:
					try:
						with open(f"{self._path}{loop}.png", "rb") as img:
							self._img_bin_list.append(img.read())
					except FileNotFoundError:
						with open(f"{self._path}{loop}.gif", "rb") as img:
							self._img_bin_list.append(img.read())

		# removing the images found in the banlist
		self._img_bin_list = [img for img in self._img_bin_list if img not in self._banlist]

		if len(self._img_bin_list) > 0:
			# creating the pdf
			try:
				with open(self._pdf_path, "wb") as pdf:
					pdf.write(img2pdf.convert(self._img_bin_list, title=self._name_metadata_pdf, author=self.fetcher.author, keywords=[self.fetcher.manga_name]))
			except Exception as e:
				# removing alpha from all the images of the chapter
				if e.args[0] == "Refusing to work on images with alpha channel":
					if not self._quiet:
						print("removing alpha...", end=" ")

					dealpha_list = []
					for img in self._img_bin_list:
						temp = Image.open(io.BytesIO(img)).convert("RGB")
						with io.BytesIO() as dealpha_img:
							temp.save(dealpha_img, format="JPEG")
							dealpha_list.append(dealpha_img.getvalue())
					with open(self._pdf_path, "wb") as pdf:
						pdf.write(img2pdf.convert(dealpha_list, title=self._name_metadata_pdf, author=self.fetcher.author, keywords=[self.fetcher.manga_name]))
				else:
					raise e

			if not self._quiet:
				print("converted")
		else:
			raise EmptyChapter(self.fetcher.manga_name, self.fetcher.chapter_number)

	def go_to_chapter(self, chap_num):
		"""
		Make Pyscandl go to the asked chapter.

		:param chap_num: chapter number that was asked for
		:type chap_num: int/str/float
		"""

		# in case windows is the os, remove the banned characters
		if os.name == "nt":
			chapter_name = re_sub(r'[\\/*?:"<>|]', u"█", self.fetcher.chapter_name)
		else:
			chapter_name = self.fetcher.chapter_name

		self.fetcher.go_to_chapter(chap_num)
		self._path = f"{self._output}ch.{self.fetcher.chapter_number} {chapter_name}/"
		self._img_bin_list = []
		# prepares the next pdf path and name
		if self._tiny:
			if isinstance(self.fetcher, StandaloneFetcher):
				self._pdf_path = f"{self._output}{chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.chapter_name}"
			else:
				self._pdf_path = f"{self._output}ch.{self.fetcher.chapter_number} {chapter_name}.pdf"
				self._name_metadata_pdf = f"ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"
		else:
			if isinstance(self.fetcher, StandaloneFetcher):
				self._pdf_path = f"{self._output}{self.fetcher.manga_name} - {chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.manga_name} - {self.fetcher.chapter_name}"
			else:
				self._pdf_path = f"{self._output}{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"

	def next_chapter(self):
		"""
		Goes to the next chapter
		"""

		self.fetcher.next_chapter()

		# in case windows is the os, remove the banned characters
		if os.name == "nt":
			chapter_name = re_sub(r'[\\/*?:"<>|]', u"█", self.fetcher.chapter_name)
		else:
			chapter_name = self.fetcher.chapter_name

		self._path = f"{self._output}ch.{self.fetcher.chapter_number} {chapter_name}/"
		self._img_bin_list = []
		# prepares the next pdf path and name
		if self._tiny:
			if isinstance(self.fetcher, StandaloneFetcher):
				self._pdf_path = f"{self._output}{chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.chapter_name}"
			else:
				self._pdf_path = f"{self._output}ch.{self.fetcher.chapter_number} {chapter_name}.pdf"
				self._name_metadata_pdf = f"ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"
		else:
			if isinstance(self.fetcher, StandaloneFetcher):
				self._pdf_path = f"{self._output}{self.fetcher.manga_name} - {chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.manga_name} - {self.fetcher.chapter_name}"
			else:
				self._pdf_path = f"{self._output}{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {chapter_name}.pdf"
				self._name_metadata_pdf = f"{self.fetcher.manga_name} - ch.{self.fetcher.chapter_number} {self.fetcher.chapter_name}"

	def full_download(self):
		"""
		Does the full download process with what is specified when initializing the Pyscandl object
		"""

		try:
			# emulating a do while
			self._skip()
			counter = 1

			try:
				if self._keep or self._image:
					self.keep_full_chapter()
				else:
					self.full_chapter()

				if not self._image:
					try:
						self.create_pdf()
					except EmptyChapter:
						if not self._quiet:
							print("empty")
			except DelayedRelease as e:
				if not self._quiet:
					print(e)

			while not isinstance(self.fetcher, StandaloneFetcher) and not self.fetcher.is_last_chapter() and (self._all or counter < self._download_number or float(self.fetcher.chapter_number) < self._chapend):
				self.next_chapter()
				try:
					if self._keep or self._image:
						self.keep_full_chapter()
					else:
						self.full_chapter()

					if not self._image:
						try:
							self.create_pdf()
						except EmptyChapter:
							if not self._quiet:
								print("empty")
				except DelayedRelease as e:
					if not self._quiet:
						print(e)
				counter += 1
		except KeyboardInterrupt:
			if not self._quiet:
				print("\nmanual interruption")
		finally:
			self.fetcher.quit()
			if not self._quiet:
				print("end of the download")
