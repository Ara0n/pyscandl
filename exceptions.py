class TooManySauce(Exception):
	def __init__(self):
		Exception.__init__(self, "too many sauce, you can't give a manga and a link at the same time !")


class DryNoSauceHere(Exception):
	def __init__(self):
		Exception.__init__(self, "you need to give either a link to the manga or its name !")


class MangaNotFound(Exception):
	def __init__(self, name):
		Exception.__init__(self, f"the manga {name} was not found")
