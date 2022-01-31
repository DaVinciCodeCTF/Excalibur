try:
	from subprocess import PIPE, run
	import codecs
	import regex as re
	import base64
	from binascii import hexlify, unhexlify
except Exception as e:
	raise ImportError("rsasolver.py -> " + str(e))


def crack(n,e,c):

	
	command = ["python3", "/usr/bin/RsaCtfTool/RsaCtfTool.py", "-n", (str)(n), "-e", (str)(e), "--uncipher", (str)(c)]
	result = run(command,stdout=PIPE, stderr=PIPE)
	try:
		s = result.stderr.split(b"STR")[1]
	except:
		s = b"Could not solve"

	return result.stderr.decode("utf-8"), s.decode("utf-8")


def rsapemcrack(file,ct):
	ct = re.sub(r"[\r\n]", "", ct)
	try:
		try:
			ct = base64.b64decode(ct)
			ct = int(hexlify(ct),16)
		except:
			ct = int(hexlify(ct),16)
	except:
		pass
	command = ["python3", "/usr/bin/RsaCtfTool/RsaCtfTool.py", "--publickey", file, "--uncipher", (str)(ct)]
	result = run(command,stdout=PIPE, stderr=PIPE)
	try:
		s = result.stderr.split(b"STR")[1]
	except:
		s = b"Could not solve"
	return result.stderr.decode("utf-8"), s.decode("utf-8")
