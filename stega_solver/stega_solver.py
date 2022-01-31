try:
	import image_solver
	import audio_solver
	import video_solver
	import text_solver
except Exception as e:
	raise ImportError("stega_solver.py -> " + str(e))


def solve(link=None,plaintext=None,path=None):
	if path:
		audio_formats=[".mp3",".wav",".midi"]
		image_formats=[".png",".jpeg"]
		video_formats=[".mp4"]
		if path.suffix in audio_formats:
			audio_solver.solve(link,path) #Add a password arg to argparse
		elif path.suffix in image_formats:
			image_solver.solve(link,path)
		elif path.suffix in video_formats:
			video_solver.solve(link,path)
	elif plaintext:
		text_solver.solve(plaintext=None)
