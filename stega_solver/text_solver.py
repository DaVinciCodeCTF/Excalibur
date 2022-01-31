try:
	import subprocess
	import os
	import unistego
	import re
	from utilities.finder import find_flag
	from utilities.utilities import check_which
	from utilities.utilities import log
	import brainfuck
	from stega_solver.malbolge_interpreter import execute
except Exception as e:
	raise ImportError("text_solver.py -> " + str(e))


#def solve(plaintext=None):
#	if not plaintext:
#		print("text_solver.py wasn't given any input")
#		exit(0)
#	#https://github.com/holloway/steg-of-the-dump/blob/master/steg-of-the-dump.js
#	"""dictionnary
#	if "\\u200" in plaintext:
#		#run js
#		pass
#	else:
#		pas
#	"""

def writeZeroWidthUnicodeMsg(secret_message, inputFile, outputFileName):
	carrier_text=open(inputFile.name, 'rt')
	hider=unistego.get_hider(open(outputFileName, 'wt'), secret_message, 'joiners')
	with carrier_text, hider:
		hider.write(carrier_text.read())

def readZeroWidthUnicodeMsg(file):
	result = ""
	try:
		unhider=unistego.get_unhider(open(file.name, 'rt'), 'joiners')
		with unhider:
			unhider.read()
		result = str(unhider.get_message().decode('utf-8'))
	except:
		pass
	if(type(result) != str): result = ""
	return result

def readSNOWmsg(file):
	#'sudo apt-get install stegsnow' pour installer le programme stegsnow
	result = ""
	try:
		if(check_which("stegsnow")):
			address = file.name
			# result = str(subprocess.check_output('stegsnow -C ' + address, shell=True))
			result = str(subprocess.run('stegsnow -C ' + address, capture_output=True, text=True, shell=True).stdout)
	except:
		pass
	if(type(result) != str): result = ""
	return result

def extractBrainfuck(plaintext):
	code = ""
	if match := re.search('[><\+\-.,\[\]]+', plaintext):
		code = match.group(0)
	return code

def readBrainfuck(verbose, challenge, plaintext):
	result = ""
	brainfuckCode = extractBrainfuck(plaintext)
	if(brainfuckCode != ""):
		challenge.log("The text might be brainfuck code, trying brainfuck (esoteric language) execution (using brainfuck interpreter)", verbose=verbose, state=2)
		try:
			f = brainfuck.to_function(brainfuckCode)
			result = str(f())
		except:
			pass
	if(type(result) != str): result = ""
	return result

def readMalbolge(plaintext):
	result = ''
	try:
		result = execute(plaintext.encode('utf-8'))
	except:
		pass
	if(type(result) != str): result = ""
	return result

def readWhitespace(file):
	result=''
	try:
		if(check_which("whitespace")):
			address = file.name
			# result = str(subprocess.check_output('whitespace ' + address, shell=True))
			result = str(subprocess.run('whitespace ' + address, capture_output=True, text=True, shell=True).stdout)
	except:
		pass
	if(type(result) != str): result = ""
	return result

def detectTwitterSecret(plaintext):
	unicodeRepr = repr(plaintext)
	hasU200 = False
	if(unicodeRepr.find(r'\u200') != -1):
		hasU200 = True
	return hasU200

def extractJSFuck(plaintext):
	code = ""
	if match := re.search('[[\]()!+]+', plaintext):
		code = match.group(0)
	return code

def evalJSFuck(tempFile):
	#'sudo apt install nodejs' pour installer NodeJS
	
	result = ""
	if(check_which("node")):
		address = tempFile.name
		try:
			
			# result = str(subprocess.check_output('node stega_solver/log_JSFck_output.js ' + address, shell=True))
			result = str(subprocess.run('node stega_solver/log_JSFck_output.js ' + address, capture_output=True, text=True, shell=True).stdout)
		except Exception as e:
			print(str(e))
	if(type(result) != str): result = ""
	return result

def readJSFuck(verbose, challenge, file, plaintext):
	result = ''
	JSFuckCode = extractJSFuck(plaintext)
	if(JSFuckCode != ""):
		challenge.log("JSFuck characters detected : the text might be JSFuck code, trying javascript execution", verbose=verbose, state=2)
		path = "/".join(file.name.split("/")[:-1])
		with open(path + "/temp_extracted_jsf_code.txt", "w") as tempFile:
			tempFile.write(JSFuckCode)
		result = evalJSFuck(tempFile)
		os.remove(path + "/temp_extracted_jsf_code.txt")
	if(result.find('eval error') != -1):
		challenge.log("JSFuck code was detected in the text content of this challenge, but its execution has failed.\nYou can try to decode it here : https://www.dcode.fr/jsfuck-language", verbose=True, state=3)
		result = ""
	return result


def solve_stegatxt(args,challenge,plaintext):
	try:
		file = open(str(challenge.directory) + "/temp_plaintext_file.txt", "w")
		file.write(plaintext)
		file.close()

		flagTrouve = False

		#on essaie de décoder du snow
		challenge.log("Trying whitespace stegano decoding (using stegsnow tool)", verbose=args.verbose, state=2)
		readResult = readSNOWmsg(file)
		if(readResult != ""):
			flagTrouve = find_flag(args.flag_format, readResult)
		
		if(not flagTrouve):
			#on essaie de décoder du zero width unicode
			challenge.log("Trying zero width unicode decoding (using unistego tool)", verbose=args.verbose, state=2)
			readResult = readZeroWidthUnicodeMsg(file)
			if(readResult != ""):
				flagTrouve = find_flag(args.flag_format, readResult)

		if(not flagTrouve):
			#on essaie d'executer du code brainfuck
			challenge.log("Trying brainfuck (esoteric language) decoding", verbose=args.verbose, state=2)
			readResult = readBrainfuck(args.verbose, challenge, plaintext)
			if(readResult != ""):
				flagTrouve = find_flag(args.flag_format, readResult)
		
		if(not flagTrouve):
			#on essaie d'executer du code malbolge
			challenge.log("Trying malbolge (esoteric language) execution (using malbolge interpreter)", verbose=args.verbose, state=2)
			readResult = readMalbolge(plaintext)
			if(readResult != ""):
				flagTrouve = find_flag(args.flag_format, readResult)

		if(not flagTrouve):
			#on essaie d'executer du code whitespace
			challenge.log("Trying whitespace (esoteric language) execution (using whitespace interpreter)", verbose=args.verbose, state=2)
			readResult = readWhitespace(file)
			if(readResult != ""):
				flagTrouve = find_flag(args.flag_format, readResult)

		if(not flagTrouve):
			#on essaie d'executer du code JSFuck
			challenge.log("Trying JSFuck (esoteric language) decoding", verbose=args.verbose, state=2)
			readResult = readJSFuck(args.verbose, challenge, file, plaintext)
			if(readResult != ""):
				flagTrouve = find_flag(args.flag_format, readResult)

		if(not flagTrouve):
			#on essaie de décoder un message codé dans des homoglyphs unicode
			challenge.log("Looking for unicode homoglyphs encoding", verbose=args.verbose, state=2)
			hasHomoglyph = detectTwitterSecret(plaintext)
			if(hasHomoglyph):
				challenge.log('Zero width space unicode character was detected : the text content might have a message hidden in it using Unicode homoglyphs. You can try to decode it here : https://holloway.nz/steg/', verbose=True, state=3)

		if(not flagTrouve):
			challenge.log("No steganographic message could be extracted from this text", verbose=True, state=2)
		os.remove(str(challenge.directory) + "/temp_plaintext_file.txt")
	
	except Exception as e:
		print(str(e))
		exit(0)