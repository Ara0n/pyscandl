from abc import ABC, abstractmethod


class Fetcher(ABC):
    __doc__ = """
    Abstract class defining how a fetcher is made and what are the mandatory components in it to be able to interact with pyscandl.
    
    The objecive of a fetcher is to gather the information specific of the manga asked in a way that it can be easily used for the creation of the downloaded scan in a pdf and/or image form.
    """

    @abstractmethod
    def __init__(self, link:str=None, manga:str=None, chapstart=1):
        """
        Initialization of the fetcher. for your fetcher to be able to work you'll need at either link or manga to be specified.

        :param link: link to the main page of the wanted scan
        :type link: str
        :param manga: unique id corresponding to the manga on the website that can be used instead of the link to access the manga
        :type manga: str
        :param chapstart: number of the first chapter of the download
        """

        self.author:str = "TBD"  #: name of the author of the manga default to TBD if none is found
        self.chapter_name:str = ""  #: name of the chapter currently in the fetcher defaults to an empty string if no name is found
        self.chapter_number = chapstart  #: number of the chapter currently in the fetcher
        self.domain:str = None  #: domain of the website the fetcher is currently on looks like: .domname.ext
        self.ext:str = None  #: extention of the image currently in the fetcher
        self.image:str = None  #: url to the image currently in the fetcher
        self.manga_name:str = None  #: name of the manga currentl in the fetcher
        self.npage:int = 1  #: number of the page the fetcher is currently on

    @abstractmethod
    def next_image(self):
        """
        Go to the next image in the current chapter.
        """

        pass

    @abstractmethod
    def go_to_chapter(self, chap):
        """
        Go to the specified chapter.

        :param chap: number of the specified chapter

        :raises MangaNotFound: the asked chapter doesn't exist
        """

        pass

    @abstractmethod
    def next_chapter(self):
        """
        Go to the next chapter in order.
        """

        pass

    @abstractmethod
    def is_last_image(self):
        """
        Checks if it's the last image in the current chapter.

        :rtype: bool
        """

        pass

    @abstractmethod
    def is_last_chapter(self):
        """
        Checks if the current chapter is the last available one

        :rtype: bool
        """

        pass

    @classmethod
    @abstractmethod
    def scan(cls, link:str=None, manga:str=None):
        """
        It is a class method to avoid initializing a fetcher with a chapter for othing, which would take time and resources for nothing.
        As a result you onnly get either the manga link or the manga id to do the method.

        Gives a list of all the chapters available for that current manga.
        The number given must correspond to the number you give to specify the chapters you want to the fetcher.
        To facilitate the usage please return a list of int and floats for the *.x* chapters.

        :param link: link of the manga
        :type link: str
        :param manga: unique id of the manga
        :type manga: str

        :rtype: list[int/float]

        :raises MangaNotFound: the asked manga doesn't exist
        """

        pass

    def quit(self):
        """
        Closes everything used by the fetcher safely.
        """

        pass


class StandaloneFetcher(ABC):
    __doc__ = """
    Abstract class defining how a standalone type fetcher is made and what are the mandatory components in it to be able to interact with pyscandl.
    
    This type of fetcher is used for the website that do not reference their scans with mangas and chapters but as standalones, an example of a website doing that is https://nhentai.net.
    """

    @abstractmethod
    def __init__(self, link:str=None, manga:str=None):
        """
        Initialization of the fetcher. for your fetcher to be able to work you'll need at either link or manga to be specified.

        :param link: link to the main page of the wanted scan
        :type link: str
        :param manga: unique id corresponding to the manga on the website that can be used instead of the link to access the manga
        :type manga: str
        """

        self.author:str = "TBD"  #: name of the author of the manga default to TBD if none is found
        self.chapter_name:str = ""  #: name of the chapter currently in the fetcher defaults to an empty string if no name is found, for standalones if the manga_name attribute is used to convey a different info you can place the manga name here, see the NHentai fetcher for an example
        self.domain:str = None  #: domain of the website the fetcher is currently on looks like: .domname.ext
        self.ext:str = None  #: extention of the image currently in the fetcher
        self.image:str = None  #: url to the image currently in the fetcher
        self.manga_name:str = None  #: name of the manga currentl in the fetcher, can be used differently as this dictates the name of the folder they are stored in, for example, the fetcher NHentaiuse this to store everything in a NSFW folder and tags them as NSFW
        self.npage:int = 1  #: number of the page the fetcher is currently on

    @abstractmethod
    def next_image(self):
        """
        Go to the next image in the current chapter.
        """

        pass

    @abstractmethod
    def is_last_image(self):
        """
        Checks if it's the last image in the current chapter.

        :rtype: bool
        """

        pass

    def quit(self):
        """
        Closes everything used by the fetcher safely.
        """

        pass
