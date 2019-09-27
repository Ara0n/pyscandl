from git import Repo


def update():
	print("checking if update is needed")
	rep = Repo("..")

	# checking if on the release tagged commit
	if not rep.tags[-1].commit == rep.head.commit:
		rep.git.checkout(rep.tags[-1])

	# comparing the last tag in the local repo to the last tag on github
	if rep.tags[-1].name == rep.git.ls_remote("--tags").split("/")[-1]:
		print("updating.", end="")
		rep.git.checkout("master")
		print(".", end="")
		rep.git.pull()
		print(".", end=" ")
		rep.git.checkout(rep.tags[-1])
		print("updated")
	else:
		print("the program is already up to date")
