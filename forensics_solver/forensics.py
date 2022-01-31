try:
	import os
	from pathlib import *
	import sys
	sys.path.insert(1, str(Path(os.path.realpath(__file__)).parents[1]))
	from utilities.finder import find_flag
	from shutil import rmtree
	from crypto_solver.Ciphey import decipher
	from PIL import Image, ExifTags
	import magic
	mime = magic.Magic(mime=True)
	from pyunpack import Archive
	import subprocess
	from utilities.utilities import clean_directory_name, check_which, timeout
except Exception as e:
	raise ImportError("forensics.py -> " + str(e))


def solve(challenge,args):
	if len(challenge.files)==0:
		challenge.log("This Forensic challenge doesn't have any files, it cannot be processed, check scraping and category assignement.",state=4)
		return False
	for file in challenge.files:
		file_analyser(args,challenge,file)
	



		
def file_analyser(args,challenge,file):
	if file.is_file():
		#Main grep
		try:
			with timeout(10):
				with open(file,encoding="utf8", errors='ignore') as f:
					#challenge.log("Grep in "+str(file.name), verbose=args.verbose)
					plaintext=f.read()
					if len(plaintext)>4:
						find_flag(verbose=args.verbose,flag_format=args.flag_format,challenge=challenge,plaintext=plaintext)
		except:
			pass
		

		try:
			with timeout(10):
				#Main strings
				strings(args,challenge,file)
				#Suffix analysis
				suffix=file.suffixes
				#Given by mime type is no suffix
				
				if len(suffix)==0:
					try:
						suffix=[mime.from_file(str(file)).lower().decode()]
						#challenge.log("Guessed suffix with mime for "+file.name+": "+suffix[0],args.verbose)
					except:
						return None
				if len(suffix)==1:
					suffix=suffix[0]
					if "txt" in suffix:
						#Hard Ciphey
						pass
					elif any(x in suffix for x in ["pcap","cap","pcapng"]):
						challenge.log("Trying to extract http objects from capture "+file.name, verbose=args.verbose, state=2)
						export_http_objects(challenge,file,args)
						#Follow TCP Stream+Ciphey
						pass
					elif any(x in suffix for x in ["doc","xls","ppt"]):
						#Oledump/Oletools
						pass
					elif "pdf" in suffix:
						challenge.log("Trying to extract hidden objects from pdf "+file.name, verbose=args.verbose, state=2)
						pdf_parser(challenge,file,args)
					elif any(x in suffix for x in ["zip","gz","7z","tar","gzip","bzip","gz","jar","rar","archive"]):
						challenge.log("Trying to extract unpack files from archive "+file.name, verbose=args.verbose, state=2)
						for child in unpack(challenge,file):
							file_analyser(args,challenge,child)
						pass
					elif any(x in suffix for x in ["png","jpg","raw","bmp","jpeg"]):
						challenge.log("Trying to binwalk the image "+file.name, verbose=args.verbose, state=2)
						if ("binwalk_" not in str(file)): #Only depth 1, can't binwalk a file that is in binwalk-created folder
							for child in binwalk_files(challenge,file):
								file_analyser(args,challenge,child)

						#OCRreader done in stega
						challenge.log("Trying to exiftool the image "+file.name, verbose=args.verbose, state=2)
						exiftool(args,challenge,file)

						challenge.log("Trying to fix header with PCRT of the image "+file.name, verbose=args.verbose, state=2)
						if "png" in suffix:
							PCRT(challenge,file)
					else:
						#do the cmd file to guess the file type
						pass
					
				elif len(suffix)==2:
					if suffix==["tar","gz"]:
						challenge.log("Trying to extract unpack files from archive "+file.name, verbose=args.verbose, state=2)
						for child in unpack(challenge,file):
							file_analyser(args,challenge,child)
		except:
			pass




def exiftool(args,challenge,file):
	try:
		log()
		img = Image.open(file)
		exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
		for k,v in exif.items():
			prop=v.split()
			if (prop & prop.Length>0):
				for word in prop:
					find_flag(verbose=args.verbose,flag_format=args.flag_format,plaintext=word,challenge=challenge)
	except:
		return None



def binwalk_files(challenge,file):
	binwalk_dir=Path(str(challenge.directory)+"/binwalk_"+clean_directory_name(file.name))
	if not binwalk_dir.is_dir(): 	#Only if we haven't binwalked the file yet
		subprocess.run(["binwalk -n 100 -C "+str(challenge.directory)+"/binwalk_"+clean_directory_name(file.name)+" --dd='.*' '"+str(file)+"'"],shell=True, stdout=subprocess.DEVNULL)
		challenge.log("### Binwalk files from "+file.name+":")
		for child_file in [x for x in binwalk_dir.glob('**/*') if x.is_file()]:
			challenge.log(child_file.name)
	return [x for x in binwalk_dir.glob('**/*') if x.is_file()]



def strings(args,challenge,file):
	proc=subprocess.check_output(["strings '"+str(file)+"'"],shell=True)
	strings=[x.decode() for x in proc.split(b"\n")]
	filtered_strings=[x for x in strings if x != '' and len(x)>5]
	for string in filtered_strings:
		find_flag(verbose=args.verbose,flag_format=args.flag_format,plaintext=string,challenge=challenge,ciphey_search=True)


def unpack(challenge,file):
	unpack_dir=Path(file.parents[0].joinpath(file.stem+"_unpacked"))
	#print('Unpacking this file:',file,"into",unpack_dir,"existence:",unpack_dir.exists()	)
	if unpack_dir.exists() and unpack_dir.is_dir():
		pass #This is not bad code, is_dir might crash if you try to do a double negative with an or
	else:
		os.mkdir(unpack_dir)
		try:
			Archive(file).extractall(unpack_dir)
			challenge.log("### Unpacked files from "+file.name+":")
			for child_file in unpack_dir.glob('**/*'):
				challenge.log(child_file.name)
		except:
			os.rmdir(unpack_dir)
			return []
	return [x for x in unpack_dir.glob('**/*') if x.is_file()]


def PCRT(challenge,file):
	try:
		from forensics_solver.pcrt import PCRT
		PCRT(None,str(file),str(file.parents[0])+"/"+str(file.name)+"pcrt_output.png")
	except Exception as e:
		print(e)



def pdf_parser(challenge, file, args):
	directory=Path(__file__).parent.absolute() 
	output=subprocess.run(["python3 "+str(directory)+"/pdf-parser.py -a "+str(file)],shell=True,capture_output=True).stdout.decode()

	challenge.log("```",clean=True)
	challenge.log(output ,args.verbose,clean=True)
	challenge.log("```",clean=True)

	if "/embeddedfile" in output.lower():
		line=[x for x in output.lower().split("\n") if "/embeddedfile" in x][0]
		number=line.split(":")[0][-1]
		objects=[x for x in line.split(": ")[1].split(", ")]
		challenge.log("We found "+number+" embedded files in objects: "+str(objects),args.verbose)
		for obj in objects:
			challenge.log("This is the embedded file object "+obj+" filtered and unfiltered:",args.verbose,clean=True)
			output=subprocess.run(["python3 "+str(directory)+"/pdf-parser.py -o "+str(obj)+" "+str(file)],shell=True,capture_output=True).stdout.decode()
			challenge.log("```",clean=True)
			challenge.log(output, args.verbose,clean=True)
			challenge.log("```",clean=True)
			find_flag(verbose=args.verbose, flag_format=args.flag_format, plaintext=output, challenge=challenge)

			output=subprocess.run(["python3 "+str(directory)+"/pdf-parser.py -f -o "+str(obj)+" "+str(file)],shell=True,capture_output=True).stdout.decode()
			challenge.log("```",clean=True)
			challenge.log(output,args.verbose,clean=True)
			challenge.log("```",clean=True)
			find_flag(verbose=args.verbose, flag_format=args.flag_format, plaintext=output, challenge=challenge)




def export_http_objects(challenge, file, args):
	if check_which("tshark"):
		export_dir=Path(str(challenge.directory), clean_directory_name(file.name + "_http_obj"))
		if not export_dir.is_dir(): 	#Only if we haven't binwalked the file yet
			os.makedirs(export_dir)
		subprocess.run(["tshark -r " + str(file) + " --export-objects \"http," + str(export_dir) + "\""],shell=True,capture_output=True)
		extracted_objs=[x for x in export_dir.glob('**/*') if x.is_file()]
		if len(extracted_objs)==0:
			challenge.log("We didn't find any HTTP objects in this capture", verbose=args.verbose)
			rmtree(str(export_dir))
		else:
			challenge.log("We extracted "+str(len(extracted_objs)) + " HTTP objects:", state=0, verbose=args.verbose)
			for extracted_obj in extracted_objs:
				challenge.log(extracted_obj.name, verbose=args.verbose)
