try:
	import subprocess
	import random
	import os
except Exception as e:
	raise ImportError("seedfinder.py -> " + str(e))

# TODO: find the right chdir, make with_array async


def get_untwister():
	os.chdir("/usr/bin/")
	subprocess.call("git clone https://github.com/altf4/untwister.git", shell = True)
	os.chdir("usr/bin/untwister")
	subprocess.call("make", shell = True)


def get_seed_with_array(array):
	file =  open("rngnumbers.txt","w+")
	for i in range(len(array)):
		file.write(str(array[i]))
		file.write("\n")
	os.chdir("/usr/bin/untwister")
	subprocess.call(["./untwister","-i","rngnumbers.txt","-r","mt19937"])


def get_seed_with_file(file):
	try:
		os.chdir("/usr/bin/untwister")
		subprocess.call(["./untwister","-i",file])
	except:
		return "failed to get file"


def get_next_numbers(array,amount):
	file =  open("rngnumbers.txt","w+")
	for i in range(len(array)):
		file.write(str(array[i]))
		file.write("\n")
	amount+= len(array)
	try:
		os.chdir("/usr/bin/untwister")
		subprocess.call(["./untwister","-i","rngnumbers.txt","-g",str(amount)])
	except:
		return "failed to get file"
