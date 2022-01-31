# -*- coding: utf-8 -*-
"""
@author: Thomas Ariza
"""
try:
	import pytesseract
	from PIL import Image, ImageShow
	import os
	from datetime import datetime
except Exception as e:
	raise ImportError("image_solver.py -> " + str(e))


def EcritureLisibleImg(img):
	"""
	Entrée : string nom de l'image (exple:"logo.png")
	Sortie : ressort l'écriture lisible de l'image (exple : image du logo de l'ESILV ------> "ESILV Leonard de Vinci")
	"""
	try:
		pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
	except Exception as e:
		print(str(e))
		exit(0)
	img=Image.open(img)
	mots = pytesseract.image_to_string(img).split("\n")
	if mots[1]=="\x0c" and mots[0]==" ":
		pass
	else:
		print(mots)
		del mots[-1]
		phrase=""
		for mot in mots:
			phrase=phrase+mot+" "
	print(phrase)
	print("\nSi incohérent, jeter un coup d'oeil à l'image")


def LSB_Channel(image_path,nb_bits,return_path):
	"""
	enregistre les 3 channels dans /media
	retourne la liste des channels créés
	"""
	image=Image.open(image_path)
	#Création des images
	channel_red=Image.new('RGB',image.size)
	channel_green=Image.new('RGB',image.size)
	channel_blue=Image.new('RGB',image.size)

	pixels=image.load()

	full_0=''
	for i in range(len(bin(pixels[0,0][0]))-nb_bits-2):
		full_0+='0'
#Boucle qui parcourt chaque pixel
	if image.mode=="RGB":
#Boucle qui parcourt chaque pixel
		for y in range(0,image.size[1]):
				for x in range(0,image.size[0]):
					r,g,b = pixels[x,y]
			
					lsbR=bin(r)[-nb_bits:]
					lsbG=bin(g)[-nb_bits:]
					lsbB=bin(b)[-nb_bits:]
			#On rajoute au pixel (x,y) la couleur qu'on souhaite dans chaque channel
					try:
						channel_red.putpixel((x,y),(int(lsbR+full_0),0,0))
						channel_green.putpixel((x,y),(0,int(lsbG+full_0),0))
						channel_blue.putpixel((x,y),(0,0,int(lsbB+full_0)))
					except:
							channel_red.putpixel((x,y),(255,255,255))
							channel_green.putpixel((x,y),(255,255,255))
							channel_blue.putpixel((x,y),(255,255,255))
	else:
		for y in range(0,image.size[1]):
				for x in range(0,image.size[0]):
					r,g,b,a = pixels[x,y]
			
					lsbR=bin(r)[-nb_bits:]
					lsbG=bin(g)[-nb_bits:]
					lsbB=bin(b)[-nb_bits:]
			#On rajoute au pixel (x,y) la couleur qu'on souhaite dans chaque channel
					try:
							channel_red.putpixel((x,y),(int(lsbR+full_0),0,0))
							channel_green.putpixel((x,y),(0,int(lsbG+full_0),0))
							channel_blue.putpixel((x,y),(0,0,int(lsbB+full_0)))
					except:
							channel_red.putpixel((x,y),(255,255,255))
							channel_green.putpixel((x,y),(255,255,255))
							channel_blue.putpixel((x,y),(255,255,255))
	liste_channel=[]
	liste_channel.append("channel_red_"+str(nb_bits)+"LSB.jpg")
	liste_channel.append("channel_green_"+str(nb_bits)+"LSB.jpg")
	liste_channel.append("channel_blue_"+str(nb_bits)+"LSB.jpg")
	#Enregistrement des images dans media
	channel_red.save(return_path+"/"+liste_channel[0])
	channel_green.save(return_path+"/"+liste_channel[1])
	channel_blue.save(return_path+"/"+liste_channel[2]) 
	return liste_channel

def LSB_bruteforce_image(image_path,nb_bits,return_path):
		#fonctionne pour stega2 et stega21 mais pas pour ch2
		image=Image.open(image_path)
		image_lsb=Image.new("RGB",image.size)
		pixels = image.load()
		full_0=''
		for i in range(len(bin(pixels[0,0][0]))-nb_bits-2):
			full_0+='0'
		if(image.mode=='RGB'):
			for y in range(0,image.size[1]):
					for x in range(0,image.size[0]):
						r,g,b=pixels[x,y]
				
						lsbR=bin(r)[-nb_bits:]
						lsbG=bin(g)[-nb_bits:]
						lsbB=bin(b)[-nb_bits:]
						try:
								image_lsb.putpixel((x,y),(int(lsbR+full_0),int(lsbG+full_0),int(lsbB+full_0)))
						except:
								image_lsb.putpixel((x,y),(255,255,255))
		else:
			for y in range(0,image.size[1]):
					for x in range(0,image.size[0]):
						r,g,b,a=pixels[x,y]
				
						lsbR=bin(r)[-nb_bits:]
						lsbG=bin(g)[-nb_bits:]
						lsbB=bin(b)[-nb_bits:]
						try:
								image_lsb.putpixel((x,y),(int(lsbR+full_0),int(lsbG+full_0),int(lsbB+full_0)))
						except:
								image_lsb.putpixel((x,y),(255,255,255))
		image_lsb.save(return_path+"/image_lsb"+str(nb_bits)+"bits.jpg")



def LSB_bruteforce_binary(image_path,nb_bits):
	image=Image.open(image_path)
	binary=''
	pixels=image.load()
	full_0=''
	for i in range(len(bin(pixels[0,0][0]))-nb_bits-2):
		full_0+='0'
	for y in range(0,image.size[1]):
		for x in range(0,image.size[0]):
				r,g,b = pixels[x,y]
				lsbR=bin(r)[-nb_bits:]
				lsbG=bin(g)[-nb_bits:]
				lsbB=bin(b)[-nb_bits:]
				binary+=lsbR+full_0+lsbG+full_0+lsbB+full_0
	return binary

def LSB_Repetition_Channel(challenge,image_path):
	medianow="mediaLSB_Channel"+str(datetime.now().hour)+"."+str(datetime.now().minute)+"."+str(datetime.now().second)
	os.mkdir(str(challenge.directory)+"/"+medianow)
	try:
		image=Image.open(str(image_path))
		pixels=image.load()
		for i in range (1,int(len(bin(pixels[0,0][0]))/2)+1):
			LSB_Channel(str(image_path), i,str(challenge.directory)+"/"+medianow)
		challenge.log("All LSB Channels saved in stega_solver/media") 
	except:
		challenge.log("image_path faux, vérifier le type du fichier")

def LSB_Repetition(challenge,image_path):
	medianow="mediaLSB"+str(datetime.now().hour)+"."+str(datetime.now().minute)+"."+str(datetime.now().second)
	os.mkdir(str(challenge.directory)+"/"+medianow)
	try:
		image=Image.open(str(image_path))
		pixels=image.load()
		for i in range (1,int(len(bin(pixels[0,0][0]))/2)+1):
			LSB_bruteforce_image(str(image_path), i,str(challenge.directory)+"/"+medianow)
		challenge.log("All LSB saved in stega_solver/media") 
	except:
		challenge.log("image_path faux, vérifier le type du fichier")

