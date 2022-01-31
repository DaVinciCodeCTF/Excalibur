try:
	from collections import Counter
	import subprocess
	from datetime import datetime
except Exception as e:
	raise ImportError("utilities.py -> " + str(e))


class MESSAGE(object):
	STATE = ("SUCCESS", "DEBUG", "INFO", "WARNING", "ERROR")


# Returns a dictionnary of letters and the number of occurences
def freq_dict(plaintext=None):
	return dict(Counter(plaintext))


def clean_directory_name(name):
	clean_ascii = ''.join([i if ord(i) < 128 else ''for i in name])
	return ''.join(['_' if i in [' ', '\\', '/', ':', '|', '<', '>', '*', '?'] else i for i in clean_ascii]) # Restricted chars


def check_which(proc_name):
	subproc = subprocess.run(["which "+str(proc_name)], shell=True, capture_output=True)
	if subproc.returncode == 0:
		if "bin" not in subproc.stdout.decode():
			log(str(proc_name)+"is not in /bin or /usr/bin",3)
		return True
	else:
		log("You don't seem to have "+str(proc_name)+" installed, try to  apt install it",4)
		return False


def log(text, state=1, clean=False):  # Append information
	if "\n" in text:
		lines=[x for x in text.split("\n") if x !="" and x !="\n"]
		for text in lines:
			logline(text, state, clean)
	else:
		logline(text, state, clean)

def logline(text, state=1, clean=False):
	if not clean:
		text = "[" + datetime.now().strftime("%H:%M:%S") + "] [" + MESSAGE.STATE[state] + "] " + text
	print(text)



try:
	import errno
	import os
	import signal
	import time
except:
	print("Could not import timeout dependencies in utilities.py")
	exit(0)

class TimeoutError(Exception):
    pass

class timeout:
	def __init__(self, seconds=1, error_message='Timeout'):
		self.seconds = seconds
		self.error_message = error_message
	def handle_timeout(self, signum, frame):
		raise TimeoutError
	def __enter__(self):
		signal.signal(signal.SIGALRM, self.handle_timeout)
		signal.alarm(self.seconds)
	def __exit__(self, type, value, traceback):
		signal.alarm(0)
