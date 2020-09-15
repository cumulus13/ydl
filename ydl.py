#!c:/SDK/Anaconda2/python.exe
#encoding:utf-8
from __future__ import print_function
import os, sys
from youtube_dl import YoutubeDL
from make_colors import make_colors
from pydebugger.debug import debug
import argparse
from pause import pause
import bitmath
import clipboard
if sys.version_info.major == 3:
	raw_input = input
	from urllib.parse import unquote
else:
	from  urllib import unquote

class ydl(object):
	def __init__(self):
		super(ydl, self)
		self.youtube = YoutubeDL()
	
	def download(self, url, download_path=os.getcwd(), download_name=None, confirm=False):
		try:
			from idm import IDMan
			dm = IDMan()
			dm.download(url, download_path, download_name, confirm=confirm)
		except:
			from pywget import wget
			if download_name:
				download_path = os.path.join(download_path, download_name)
			wget.download(url, download_path)
		
	def get_info(self, url):
		result = self.youtube.extract_info(url, download=False)
		return result
		
	def nav(self, url, download_path=os.getcwd(), download_name=None, confirm=False):
		result = self.get_info(url)
		n = 1
		print(make_colors("Name", 'lc') + "       : " + make_colors(result.get('title'), 'lw', 'bl'))
		print(make_colors("Description", 'lg') + ": " + make_colors(result.get('description').encode('utf-8'), 'b', 'lg'))
		for f in result.get('formats'):
			if len(str(n)) == 1:
				number = '0' + str(n)
			else:
				number = str(n)
			if f.get('filesize'):
				print(make_colors(number, 'lc') + ". " + make_colors(f.get('format'), 'lw', 'bl') + " [" + make_colors(str("%0.2f"%bitmath.Bit(f.get('filesize')).Mb) + " Mb", 'b','ly') + "] [" + make_colors(f.get('ext'), 'lr', 'lw') + "]")
			else:
				print(make_colors(number, 'lc') + ". " + make_colors(f.get('format'), 'lw', 'bl') + " [ ] [" + make_colors(f.get('ext'), 'lr', 'lw') + "]")
			n +=1
		q = raw_input(make_colors("select number: ", 'lw','lr'))
		if q and str(q).strip().isdigit():
			q = int(str(q).strip())
			if q <= len(result.get('formats')):
				link = result.get('formats')[q - 1].get('url')
				clipboard.copy(link)
				debug(link = link, debug = True)
				download_name = result.get('title') + "." + result.get('ext')
				self.download(link, download_path, download_name, confirm)
			
			
if __name__ == '__main__':
	c = ydl()
	if not len(sys.argv) > 1:
		print(make_colors("Usage:", 'lw', 'lr') + " " + make_colors("ydl.py [URL]", 'lw', 'lb'))
	else:
		url = sys.argv[1]
		if url == 'c':
			url = clipboard.paste()
		c.nav(url)