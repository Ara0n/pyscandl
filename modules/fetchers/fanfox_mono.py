from .fanfox import Fanfox


class FanfoxMono(Fanfox):
	def __init__(self, link: str = None, manga: str = None, chapstart: int = 1):
		print("deprecated please use FANFOX instead")
		super().__init__(link, manga, chapstart)
