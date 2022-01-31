try:
	import os
	from pathlib import *
	import sys
	sys.path.insert(1, str(Path(os.path.realpath(__file__)).parents[1]))
	import subprocess
	from utilities.finder import find_flag
	import magic
	mime = magic.Magic(mime=True)
	from stega_solver.image_solver import LSB_Repetition, LSB_Repetition_Channel
	from stega_solver.audio_solver import graph_spectrogram, dtmf
	from stega_solver.text_solver import solve_stegatxt
	from utilities.utilities import check_which
	import re
except Exception as e:
	raise ImportError("stega.py -> " + str(e))


def solve(challenge,args):
	
	if len(challenge.files)==0:
		challenge.log("This Stegano challenge doesn't have any files, its description will be analyzed instead.")
		solve_stegatxt(args,challenge,str(challenge.desc))

	for file in challenge.files:
		file_analyser(args,challenge,file)




def file_analyser(args,challenge,file):
	possible_pass = [""]
	possible_pass += challenge.name.split()
	possible_pass += challenge.desc.split()
	success_steghide = False
	success_outguess = False
	if file.is_file():
		#Main grep
		with open(file,encoding="utf8", errors='ignore') as f:
			find_flag(verbose=args.verbose,flag_format=args.flag_format,challenge=challenge,plaintext=f.read())

		#Main strings
		strings(args,challenge,file)
	
		#Suffix analysis
		suffix=file.suffixes
		#Given by mime type is no suffix
		if len(suffix)==0:
			try:
				suffix=[mime.from_file(str(file)).lower().decode()]
				challenge.log("Guessed suffix with mime for "+file.name+": "+suffix[0],args.verbose)
			except:
				return None
		if len(suffix)==1:
			suffix=suffix[0]
			if "txt" in suffix:
				#Hard Ciphey
				solve_stegatxt(args,challenge,str(file.open().read()))
			elif any(x in suffix for x in ["png","jpg","raw","bmp","jpeg"]):
				if check_which("foremost"):
					foremost_file(challenge,file)
				if check_which("zsteg"):
					zsteg_file(args,challenge,file)
				if check_which("steghide"):
					# steghide_file(args,challenge,file,"")
					for p in possible_pass:
						success_steghide = steghide_file(args,challenge,file,p)
						if success_steghide:
							break
				if check_which("outguess"):
					# outguess_file(challenge,file,"")
					for p in possible_pass:
						success_outguess = outguess_file(challenge,file,p)
						if success_outguess:
							break
				LSB_Repetition(challenge,file)
				LSB_Repetition_Channel(challenge,file)
			elif any(x in suffix for x in [".wav",".mp3",".aac"]):
				graph_spectrogram(challenge,file)
				dtmf(challenge,file)
			elif any(x in suffix for x in [".avi",".mp4",".mkv"]):
				if check_which("ffmpeg"):
					ffmpeg(args,challenge,file)
				subprocess.run(["ffmpeg -loglevel panic -i "+str(file)+" "+str(file.parent)+"/ffmpeg_"+(str(file.name)).split(".")[0]+".mp3"],shell=True,stdout=subprocess.DEVNULL)
				file_mp3 = open(str(file.parent)+"/ffmpeg_"+(str(file.name)).split(".")[0]+".mp3")
				#graph_spectrogram(file_mp3)
			else:
				#do the cmd file to guess the file type
				pass
		elif len(suffix)==2:
			if suffix==["tar","gz"]:
				pass



def zsteg_file(args,challenge,file):
	if file.suffix==".png":
		subprocess.run(["zsteg "+str(file)+" > "+str(file.parent)+"/zsteg_"+file.name+".txt"],shell=True,stdout=subprocess.DEVNULL)
		fzsteg=open(str(file.parent)+"/zsteg_"+file.name+".txt",encoding="utf8", errors='ignore')
		contentszsteg = fzsteg.read()
		for i in contentszsteg.split():   
			find_flag(verbose=args.verbose,flag_format=args.flag_format,plaintext=i,challenge=challenge)

def steghide_file(args,challenge,file,password=""):
	if password == "":
		password = file.name.split(".")[0]
	success = False
	if file.suffix!=".png":
		try:
			output = subprocess.check_output(["steghide extract -q -sf "+str(file)+" -p "+str(password)+" -xf "+str(file.parent)+"/steghide_"+file.name+".txt"],shell=True,stderr=subprocess.STDOUT).decode()
			# output = subprocess.run(["steghide extract -sf "+str(file)+" -p "+str(password)+" -xf "+str(file.parent)+"/steghide_"+file.name+".txt"],shell=True,capture_output=True).stdout.decode()
			success = True
			fsteghide=open(str(file.parent)+"/steghide_"+file.name+".txt",encoding="utf8", errors='ignore')
			contentssteghide = fsteghide.read()
			for i in contentssteghide.split():
				find_flag(verbose=args.verbose,flag_format=args.flag_format,plaintext=i,challenge=challenge)
		except subprocess.CalledProcessError as e:
			output = e.output.decode()
			success = False
	return success	

def outguess_file(challenge,file,password=""):
	if password == "":
		password=file.name.split(".")[0]
	subprocess.run(["outguess -k "+str(password)+" -r "+str(file)+" "+str(file.parent)+"/outguess_"+file.name],shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	# output = subprocess.check_output(["file "+str(file.parent)+"/outguess_"+file.name],shell=True,stderr=subprocess.STDOUT)
	output = subprocess.run(["file "+str(file.parent)+"/outguess_"+file.name],shell=True,capture_output=True).stdout.decode()
	success = ("JPEG" in output)
	if success:
		challenge.log("### Outguess files saved in "+str(file.parent)+"/outguess_"+file.name)
	return success

def foremost_file(challenge,file):
	subprocess.run(["foremost -Q -T -i "+str(file)+" -o "+str(file.parent)+"/foremost_"+file.name],shell=True,stdout=subprocess.DEVNULL)
	challenge.log("Extracted Foremost files saved in "+str(file.parent)+"/foremost_"+file.name)

def strings(args,challenge,file):
	proc=subprocess.check_output(["strings '"+str(file)+"'"],shell=True)
	strings=[x.decode() for x in proc.split(b"\n")]
	filtered_strings=[x for x in strings if x != '' and len(x)>5]
	for string in filtered_strings:
		find_flag(verbose=args.verbose,flag_format=args.flag_format,plaintext=string,challenge=challenge)

def ffmpeg(args,challenge,file):
	subprocess.run(["ffmpeg -loglevel panic -i "+str(file)+" -map 0:s:0 "+str(file.parent)+"/ffmpeg_"+(str(file.name)).split(".")[0]+".srt"],shell=True,stdout=subprocess.DEVNULL)
	fffmpeg = open(str(file.parent)+"/ffmpeg_"+(str(file.name)).split(".")[0]+".srt")
	# fffmpeg = re.sub('<?(.*?)>','',str(fffmpeg), flags=re.DOTALL)
	lignes = fffmpeg.readlines()
	for i in lignes:
		if i!="\n":
			if "-->" not in i:
				i = str(i)
				i = re.sub('<f(.*?)>','',i, flags=re.DOTALL)
				i = re.sub('</(.*?)>','',i, flags=re.DOTALL)
				i = re.sub('<i(.*?)>','',i, flags=re.DOTALL)
				find_flag(verbose=args.verbose,flag_format=args.flag_format,plaintext=i,challenge=challenge)

