try:
	import regex as re
	import enchant
except Exception as e:
	raise ImportError("pattern.py -> " + str(e))


regex_url = r"(?i)\b((?:h(xx|tt)ps?://|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))))+(?:(([^\s()<>]+|(([^\s()<>]+))))|[^\s`!()[]{};:'\".,<>?«»“”‘’]))"
#regex_domain = r'([a-z0-9]+(-[a-z0-9]+).)+[a-z]{2,}'
regex_domain = r"\b([a-z0-9]+(-[a-z0-9]+).)+[a-z]{2,}\b"
regex_md5 = r'(?i)(?<![a-z0-9])[a-f0-9]{32}(?![a-z0-9])'
regex_sha1 = r'(?i)(?<![a-z0-9])[a-f0-9]{40}(?![a-z0-9])'
regex_sha256 = r'(?i)(?<![a-z0-9])[a-f0-9]{64}(?![a-z0-9])'
regex_rsa = r'(?i)((?<![a-z0-9])\w{1,10}(?![a-z0-9]))([=: ]+)(\w+(?![\w]))'

def contains_md5(plaintext):
	return len(re.findall(regex_md5,plaintext)) == 1


def contains_sha1(plaintext):
	return False

def contains_sha256(plaintext):
	return False

def contains_url(plaintext):
	return True

def is_netcat(plaintext):
	#replace("-p ","")
	return True



def is_ssh(plaintext):
	return True

'''def rsa(plaintext):
	found = re.findall([0-9]+,plaintext)
	if len(found) ==3:
		return found
	else:
		return "False"
'''


def findcryptotype(plaintext):
	if len(re.findall(regex_md5,plaintext)) > 0:
		return "md5" , re.findall(regex_md5,plaintext)[0]

	if len(re.findall(r'[0-9]+',plaintext)) == 3:
		return "rsa" , re.findall(r'[0-9]+',plaintext)

	return 'ciphey', getNonEnglishWords(plaintext)
	













'''
def rsa(plaintext):
	#replace(";","\n"),replace(",","\n")
	#split("\n")
	for lines in lines:
		#regex pour le premier \w, (\D*)(\d+)
	return dict{"n":n,"c":c,"e":e}
'''


def gethash(plaintext):
	if contains_md5(plaintext):
		return re.findall(regex_md5,plaintext)[0]

	if contains_sha1(plaintext):
		return re.findall(regex_sha1,plaintext)[0]

	if contains_sha256(plaintext):
		return re.findall(regex_sha256,plaintext)[0]

	else:
		return "False"


def getEnglishWords(plaintext):
	toreturn = ""
	d = enchant.Dict("en_US")
	s = re.sub(r"[^\w\s'{} ]", '',plaintext)
	text = s.split(' ')
	

	for word in text:
		
		if d.check(word):
			toreturn += word + " "

	return toreturn


def getNonEnglishWords(plaintext):
	toreturn = ""
	d = enchant.Dict("en_US")
	s = re.sub(r"[^\w\s'{}=/+]",'',plaintext)
	text = s.split(' ')

	for word in text:
		
		if not d.check(word):
			toreturn += word + " "

	return toreturn


