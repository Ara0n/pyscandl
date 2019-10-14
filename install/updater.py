import os
import sys
import requests
from git import Repo
from git.exc import InvalidGitRepositoryError


def update():
	try:
		rep = Repo(os.path.dirname(sys.modules['__main__'].__file__))
		rep.git.checkout("master")
		rep.git.pull()
		rep.git.checkout(rep.tags[-1])
	except InvalidGitRepositoryError:
		latest = requests.get("https://github.com/Ara0n/pyscandl/releases/latest").url.split("/")[-1]
		print(f"you haven't installed it from the repo so you can't auto update with this command\nthe latest release is the v{latest}")
