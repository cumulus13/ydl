#!c:/SDK/Anaconda2/python.exe
#encoding:utf-8
from __future__ import print_function
import os, sys
from youtube_dl import YoutubeDL
from make_colors import make_colors
from pydebugger.debug import debug
#import argparse
import re
import bitmath
import clipboard
if sys.version_info.major == 3:
    raw_input = input
    from urllib.parse import unquote
else:
    from  urllib import unquote
import getpass
from xnotify import notify as notif
from configset import configset
import click

class ydl(object):

    youtube = YoutubeDL()
    notify = notif()
    configfile = os.path.join(os.path.dirname(__file__), 'ydl.ini')
    config = configset(configfile)
    is_playlist = False

    def __init__(self):
        super(ydl, self)
        self.youtube = YoutubeDL()

    @classmethod
    def downloader(cls, url, download_path = None, saveas = None, confirm = False):
        debug(download_path = download_path)
        if os.getenv('DOWNLOAD_PATH'):
            download_path = os.getenv('DOWNLOAD_PATH')
        debug(download_path = download_path)
        if not download_path:
            download_path = cls.config.get_config('DOWNLOAD', 'path', os.getcwd())
            debug(download_path = download_path)
        if 'linux' in sys.platform:
            if not os.path.isdir(download_path):
                this_user = getpass.getuser()
                login_user = os.getlogin()
                debug(login_user = login_user)
                this_uid = os.getuid()
                download_path = r"/home/{0}/Downloads".format(login_user)
                debug(download_path = download_path)
                if not os.path.isdir(download_path):
                    try:
                        os.makedirs(download_path)
                    except OSError:
                        print(make_colors("Permission failed make dir:", 'lw', 'lr', ['blink']) + " " + make_colors(download_path, 'lr', 'lw'))
        try:
            if not os.path.isdir(download_path):
                download_path = os.getcwd()
        except:
            download_path = None
            pass

        if not download_path:
            download_path = os.getcwd()
        if not os.access(download_path, os.W_OK|os.R_OK|os.X_OK):
            print(make_colors("You not have Permission save to dir:", 'lw', 'lr' + " " + make_colors(download_path, 'lr', 'lw')))
            download_path = os.getcwd()
        print(make_colors("DOWNLOAD PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'lw', 'lr'))

        debug(url = url)
        cls.download(url, download_path, saveas, confirm)
        icon = None
        if os.path.isfile(os.path.join(os.path.dirname(__file__), 'logo.png')):
            icon = os.path.join(os.path.dirname(__file__), 'logo.png')

        cls.notify.notify("Download finish: ", saveas, "Neonime", "FINISH", iconpath = icon)

        return url

    @classmethod
    def download_linux(cls, url, download_path=os.getcwd(), saveas=None, downloader = 'aria2c'):
        '''
            downloader: aria2c, wget, uget, persepolis
        '''
        aria2c = os.popen3("aria2c")
        wget = os.popen3("wget")
        persepolis = os.popen3("persepolis --help")

        if downloader == 'aria2c' and not re.findall("not found\n", aria2c[2].readlines()[0]):
            if saveas:
                saveas = '-o "{0}"'.format(saveas)
            os.system('aria2c -c -d "{0}" "{1}" {2} --file-allocation=none'.format(os.path.abspath(download_path), url, saveas))
        elif downloader == 'wget' and not re.findall("not found\n", wget[2].readlines()[0]):
            if saveas:
                saveas = '-P {0} -o "{1}"'.format(os.download_path.abspath(download_path), saveas)
            else:
                saveas = '-P {0}'.format(os.download_path.abspath(download_path))
            os.system('wget -c "{2}" {1}'.format(url, saveas))
        elif downloader == 'persepolis'  and not re.findall("not found\n", persepolis[2].readlines()[0]):
            os.system('persepolis --link "{0}"'.format(url))
        else:
            try:
                from pywget import wget as d
                d.download(url, download_path, saveas)
            except:
                print(make_colors("Can't Download this file !, no Downloader supported !", 'lw', 'lr', ['blink']))
                clipboard.copy(url)

    @classmethod
    def download(cls, url, download_path=os.getcwd(), download_name=None, confirm=False):
        if sys.platform == 'win32':
            try:
                from idm import IDMan
                dm = IDMan()
                dm.download(url, download_path, download_name, confirm=confirm)
            except:
                from pywget import wget
                if download_name:
                    print(make_colors("Download Name:", 'lw', 'bl') + " " + make_colors(download_name, 'lw', 'm'))
                    download_path = os.path.join(download_path, download_name)
                wget.download(url, download_path)
        elif 'linux' in sys.platform:
            return cls.download_linux(url, download_path, download_name)
        else:
            print(make_colors("Your system not supported !", 'lw', 'lr', ['blink']))

    @classmethod
    def get_info(cls, url):
        if 'list=PL' in url:
            cls.is_playlist = True
        try:
            result = cls.youtube.extract_info(url, download=False)
            return result
        except:
            return False
    
    @classmethod
    def get_download(cls, entry, quality = None, download_name = None, confirm = False, download_all = False, ext = 'mp4', show_description = True):
        qp = None
        quality_str = None
        if not ext:
            ext = "mp4"
        if download_all and not quality:
            qp = raw_input("QUALITY: ", 'lw', 'lr')
        if qp:
            quality = qp
        all_formats = entry.get('formats')
        link = None
        n = 1
        if not all_formats:
            print(make_colors("No Download Links !", 'lw', 'lr', ['blink']))
            sys.exit()
        if show_description:
            print(make_colors("Name", 'lc') + "       : " + make_colors(entry.get('title'), 'lw', 'bl'))
            description = entry.get('description')
            if description:
                print(make_colors("Description", 'lg') + ": " + make_colors(description.encode('utf-8'), 'b', 'lg'))        
        if not quality:
            for f in all_formats:
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
                if q <= len(all_formats):
                    link = all_formats[q - 1].get('url')
                    quality_str = all_formats[q - 1].get('format_note')
                    ext = all_formats[q - 1].get('ext')
                    if not download_name:
                        download_name = all_formats[q - 1].get('title')
                    clipboard.copy(link)
                    if confirm and not sys.platform == 'win32':
                        qd = raw_input(make_colors("Download with name:", 'lw', 'bl') + " " + make_colors(download_name, 'lr', 'lw') + " [y/enter] ?: ")
                        if not qd == 'y':
                            sys.exit(make_colors("Exit ...", 'lr'))                    
                    return link, quality_str, ext
            
        else:            
            for i in all_formats:
                if not download_name:
                    download_name = i.get('title')                
                if str(quality).lower() in i.get('format_note') and i.get('ext') == 'mp4':
                    link = i.get('url')
                    quality_str = i.get('format_note')
                    ext = i.get('ext')                    
                    break
            if not link:
                print(make_colors("No Quality FOUND !", 'lw', 'lr', ['blink']))
                return False
            clipboard.copy(link)
            if confirm and not sys.platform == 'win32':
                qd = raw_input(make_colors("Download with name:", 'lw', 'bl') + " " + make_colors(download_name, 'lr', 'lw') + " [y/enter] ?: ")
                if not qd == 'y':
                    sys.exit(make_colors("Exit ...", 'lr'))                                
            return link, quality_str, ext
        return False

    # @classmethod
    @click.command()
    @click.argument('url')
    @click.option('-p', '--path', help = 'Download Path', default = os.getcwd(), metavar='DOWNLOAD_PATH')
    @click.option('-o', '--output', help = 'Save as download file', metavar="NAME")
    @click.option('-q', '--quality', help = 'Quality: 240p|360p|480p|720p|1080p', metavar='QUALITY')
    @click.option('-s', '--show', help = 'Show Description for one download and false for download all', is_flag = True)
    @click.option('-c', '--confirm', help = 'Confirmation before download', is_flag = True)
    def nav(url, path, output, quality, confirm, show):
        # debug(url = url, debug = True)
        # debug(path = path, debug = True)
        # debug(output = output, debug = True)
        # debug(quality = quality, debug = True)
        ext = None
        quality_str = None
        self = ydl()
        q = None
        if url == 'c':
            url = clipboard.paste()
        result = self.get_info(url)
        if not result:
            print(make_colors("Failed to extract Video file ...", 'lw', 'lr', ['blink']))
            return False
        n = 1
        if not self.is_playlist:
            print(make_colors("Name", 'lc') + "       : " + make_colors(result.get('title'), 'lw', 'bl'))
            description = result.get('description')
            if description:
                print(make_colors("Description", 'lg') + ": " + make_colors(description.encode('utf-8'), 'b', 'lg'))
        if self.is_playlist:
            for i in result.get('entries'):
                if len(str(n)) == 1:
                    number = '0' + str(n)
                else:
                    number = str(n)
                print(\
                    make_colors(number, 'lc') + ". " +\
                    make_colors(i.get('title'), 'lw', 'bl') + " [" +\
                    make_colors(str(i.get('duration') / 60) + " minutes", 'lw', 'm') + "]"\
                )
                n += 1
            q = raw_input(make_colors("select number [a|all = download all]: ", 'lw','lr'))    
        
        link = None
        download_all = False
        
        if self.is_playlist and q:
            if q and str(q).strip().isdigit():
                q = str(q).strip()
                if not int(str(q).strip()) > len(result.get('entries')):
                    entry = result.get('entries')[int(q) - 1]
                    link, quality_str, ext = self.get_download(entry, quality, confirm)
            elif str(q).strip() == 'a' or str(q).strip() == 'all':
                download_all = True
        else:
            link, quality_str, ext = self.get_download(result, quality, confirm)
        
        if download_all:
            for i in result.get('entries'):
                link, quality_str, ext = self.get_download(i, quality, confirm = confirm, download_all = True, show_description = show)
                if not link:
                    print(make_colors("Ivalid Link !", 'lw', 'lr', ['blink']))
                else:
                    if os.getenv('TEST'):
                        print(make_colors("Downloading {}.{} [{}]  ...".format(i.get('title'), ext, quality_str)))
                    else:
                        print(make_colors("Downloading {}.{} [{}]  ...".format(i.get('title'), ext, quality_str)))
                        self.downloader(link, path, download_name, confirm)        
        else:
            if not link:
                print(make_colors("Ivalid Link !", 'lw', 'lr', ['blink']))
                return False

            debug(link = link, debug = True)
            download_name = result.get('title') + "." + ext
            if output:
                download_name = output
            if os.getenv('TEST'):
                print(make_colors("Downloading {} [{}]...".format(download_name, quality_str)))
            else:
                print(make_colors("Downloading {} [{}] ...".format(download_name, quality_str)))
                self.downloader(link, path, download_name, confirm)        
        return True

if __name__ == '__main__':
    c = ydl()
    if not len(sys.argv) > 1:
        print(make_colors("Usage:", 'lw', 'lr') + " " + make_colors("ydl.py [URL]", 'lw', 'lb'))
    else:
        # url = sys.argv[1]
        # if url == 'c':
        #     url = clipboard.paste()
        c.nav()
        # ydl.nav()