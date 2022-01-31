try:
	import crypto_solver.seedfinder
	import crypto_solver.hashcrack as hashcrack
	import crypto_solver.Ciphey as Ciphey
	import utilities.pattern as pattern
	from utilities.finder import find_flag
	import crypto_solver.rsasolver as rsasolver
	import re
except Exception as e:
	raise ImportError("cryptodispatcher.py -> " + str(e))


def solve(challenge, args):
	if len(challenge.files)<1:
		solvev2(challenge, args, challenge.desc)
		
	for file in challenge.files:
		
		Type, ToBeParsed = filescraper(file)
		
		if Type == "None":
			solvev2(challenge, args, ToBeParsed)

		else:

			challengetype, ToBeSolved = pattern.findcryptotype(challenge.desc)
			stdout , solved = rsasolver.rsapemcrack(file,ToBeSolved)
				
			challenge.log("this is solved: " + solved)
			challenge.log("this is stdout: " + stdout)
			challenge.log(solved)

			return find_flag(args.flag_format,plaintext = solved, challenge = challenge)




def solvev2(challenge, args, ToBeParsed):
	
		
		challengetype, ToBeSolved = pattern.findcryptotype(ToBeParsed)
		if challengetype == "md5":
			challenge.log(f"Sending {ToBeSolved} to hashcrack")
			solved = hashcrack.hashcracker(ToBeSolved)
			
			if not solved  == "False":
				solved = args.flag_format[:-1] + solved + "}"
				challenge.log("this is solved: " + solved)
				challenge.log(solved)
				return find_flag(args.flag_format,plaintext = solved, challenge = challenge)
				
			challenge.log("Hash not in database")
		if challengetype == "rsa":
			challenge.log(f"Sending {ToBeSolved} to rsactftool")

			stdout , solved = rsasolver.crack(ToBeSolved[0],ToBeSolved[1],ToBeSolved[2])
			

			challenge.log("this is solved: " + solved)
			challenge.log("this is stdout: " + stdout)
			challenge.log(solved)

			return find_flag(args.flag_format,plaintext = solved, challenge = challenge)

		else:
			challenge.log(f"Sending {ToBeSolved} to ciphey")

			solved = Ciphey.mainDecipher(ToBeSolved, 10)
			challenge.log("this is solved: " + str(solved))
			if not solved == None:
				challenge.log(solved)
				return find_flag(args.flag_format,plaintext = solved, challenge = challenge)








def filescraper(file):

	if ".pem" in str(file):
		return file, "rsapem"
	with open(file, 'r') as file:
		data = file.read().replace('\n', ' ')
	return data, "None"





