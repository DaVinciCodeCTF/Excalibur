try:
	import requests
	import json
	import hashlib
	import re
except Exception as e:
	raise ImportError("hashcrack.py -> " + str(e))


def hashcracker(ct):
	try:
		response = requests.get("http://some_vps_running_hash_cracking_with_tables_from_crackstations", data = ct)
		if response.text == "Hash not in database":
			return "False"
		else:
			return response.text.split(': ')[1]
	except:
		return "Could not connect to server"


def php_magic_hash(ct):
	try:
		return ct[0] == "0" and ct[1] == "e"
	except:
		return "Hash wrong format"


def php_magic_hash_reverse(ct):
	hash_types = {"sha1" : hashlib.sha1(ct).hexdigest() , "sha224": hashlib.sha224(ct).hexdigest() , "sha256": hashlib.sha256(ct).hexdigest(), "sha384":hashlib.sha384(ct).hexdigest() , "sha512":hashlib.sha512(ct).hexdigest() , "MD5":hashlib.md5(ct).hexdigest()}
	try:
		for t in hash_types:
			if php_magic_hash(hash_types[t]):
				return	("this is magic " + t + ": " + hash_types[t])
		return "Not magic php hash"
	except:
		return "Not magic php hash"


#def hashup():
#	r = requests.get("https://hashes.org/api.php?key=" + hash_api_key)
#	return	r.status_code == 200

def hashcheck(ct):

	plain = bytes(hashcracker(ct)["plain"], 'utf-8')
	hashes = {"SHA1" : hashlib.sha1(plain).hexdigest() , "SHA224": hashlib.sha224(plain).hexdigest() , "SHA256": hashlib.sha256(plain).hexdigest(), "SHA384":hashlib.sha384(plain).hexdigest() , "SHA512":hashlib.sha512(plain).hexdigest() , "MD5PLAIN":hashlib.md5(plain).hexdigest()}
	hashtype = hashcracker(ct)["algorithm"]
	try:
		return 	hashes[hashtype] == ct
	except:
		return "Could not verify the hash (type not supported)"






