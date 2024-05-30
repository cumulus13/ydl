from make_colors import make_colors
import os
from pydebugger.debug import debug
import bitmath
from pathlib import Path
from configset import configset
import traceback
from datetime import datetime
import sys
if sys.version_info.major == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
import requests
from parserheader import Parserheader
import clipboard
from unidecode import unidecode
from xnotify import notify
import re
import mimetypes

configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ydl.ini')
CONFIG = configset(configfile)

def get_header_value(headers, pattern):
    compiled_pattern = re.compile(pattern, re.I)
    for key, value in headers.items():
        if compiled_pattern.search(key):
            return value
    return None

def get_name(url: str | None = '', headers: dict | None = {}) -> list:
    if not url or not headers:
        return '', ''
    file_name = ""
    ext = ''
    if not headers:
        a = requests.get(url, stream = True)
        headers = a.headers
    if get_header_value(headers, 'content-disposition'):
        pattern = r'filename="(.+?)"'
        match = re.search(pattern, get_header_value(headers, 'content-disposition'))
        if match:
            file_name = match.group(1)
            file_name = re.sub(r'%([0-9A-Fa-f]{2})', lambda x: chr(int(x.group(1), 16)), file_name)
            ext = os.path.splitext(file_name)
            if len(ext) == 2:
                ext = ext[1]
            else:
                ext = ''
            return [file_name, ext]
        else:
            print('No file name found in the header item.')
            return 

    if get_header_value(headers, 'content-type'):
        ext = mimetypes.guess_all_extensions(get_header_value(headers, 'content-type'))
    return ['', ext]

def logger(message, status="info"):
    logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(CONFIG.configname).split(".")[0] + ".log")
    if not os.path.isfile(logfile):
        lf = open(logfile, 'wb')
        lf.close()
    real_size = bitmath.getsize(logfile).kB.value
    max_size = CONFIG.get_config("LOG", 'max_size')
    debug(max_size = max_size)
    if max_size:
        debug(is_max_size = True)
        try:
            max_size = bitmath.parse_string_unsafe(max_size).kB.value
        except:
            max_size = 0
        if real_size > max_size:
            try:
                os.remove(logfile)
            except:
                print("ERROR: [remove logfile]:", traceback.format_exc())
            try:
                lf = open(logfile, 'wb')
                lf.close()
            except:
                print("ERROR: [renew logfile]:", traceback.format_exc())


    str_format = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S.%f") + " - [{}] {}".format(status, message) + "\n"
    with open(logfile, 'ab') as ff:
        if sys.version_info.major == 3:
            ff.write(bytes(str_format, encoding='utf-8'))
        else:
            ff.write(str_format)

def downloader(url, download_path = None, saveas = None, confirm = False, ext = None, copyurl_only = False, nodownload = False, thumb = None):
    download_path0 = download_path
    url_download = None
    saveas0 = saveas
    if ext: ext = ext.lower()
    debug(ext = ext)
    debug(download_path = download_path)    
    debug(saveas = saveas)
    error = False

    try:
        if not Path(download_path).is_dir() and not copyurl_only:
            download_path = None
    except:
        pass

    if not download_path and not copyurl_only and not nodownload:
        if os.getenv('DOWNLOAD_PATH'): download_path = os.getenv('DOWNLOAD_PATH')
        if CONFIG.get_config('DOWNLOAD', 'path', os.getcwd()):
            download_path = CONFIG.get_config('DOWNLOAD', 'path')
            debug(download_path_config = download_path)
    debug(download_path0 = download_path)

    if not copyurl_only and not nodownload:
        print(make_colors("DOWNLOAD_PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))

    if not download_path and not copyurl_only and not nodownload:
        download_path = ''

    if 'linux' in sys.platform and download_path and not os.path.isdir(download_path) and not copyurl_only and not nodownload:

        debug(download_path0 = download_path)
        if not os.path.isdir(download_path):
            #this_user = getpass.getuser()
            login_user = os.getlogin()
            env_user = os.getenv('USER')
            debug(login_user = login_user)
            debug(env_user = env_user)
            #this_uid = os.getuid()
            download_path = r"/home/{0}/Downloads".format(login_user)
            debug(download_path = download_path)

    if download_path and not os.path.isdir(download_path) and not copyurl_only and not nodownload:
        try:
            os.makedirs(download_path)
        except:
            pass

    if download_path and not os.path.isdir(download_path) and not copyurl_only and not nodownload:
        try:
            os.makedirs(download_path)
        except OSError:
            tp, tr, vl = sys.exec_info()
            debug(ERROR_MSG = vl.__class__.__name__)
            if vl.__class__.__name__ == 'OSError':
                print(make_colors("Permission failed make dir:", 'lw', 'lr') + " " + make_colors(download_path, 'lr', 'lw'))


    if not download_path and not copyurl_only and not nodownload:
        download_path = os.getcwd()
    if download_path and not os.access(download_path, os.W_OK|os.R_OK|os.X_OK) and not copyurl_only:
        print(make_colors("You not have Permission save to dir:", 'lw', 'lr' + " " + make_colors(download_path, 'lr', 'lw')))
        download_path = os.getcwd()
    if not copyurl_only and not nodownload:
        print(make_colors("DOWNLOAD PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'lw', 'lr'))
    debug(download_path = download_path)
    debug(url = url)

    try:
        from idm import IDMan
        d = IDMan()
    except:
        from pywget import wget as d
    name = None
    cookies = {}

    debug(copyurl_only = copyurl_only)

    debug(netloc = urlparse(url).netloc)

    print(make_colors("DOWNLOAD LINK:", 'b', 'lc') + " " + make_colors(url, 'b', 'ly'))

    if 'solidfiles' in urlparse(url).netloc:
        try:
            from solidfiles import Solidfiles
            url_download, url_stream, info = Solidfiles.get(url)
        except:
            print(make_colors("ERROR: [solidfiles]", 'lw', 'r') + " " + traceback.format_exc())
            error = True

    elif 'dutrag' in urlparse(url).netloc or "unityplayer" in urlparse(url).netloc:
        try:
            from dutrag import Dutrag
            url_download, savename, savesize = Dutrag.generate(url)
            debug(url_download = url_download)
            debug(savename = savename)
            debug(savesize = savesize)
            if url_download:
                url_download = url_download.get('data')[0].get('file')
                debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True

    elif 'mega.nz' in urlparse(url).netloc:
        print(make_colors("URL to Generate:", 'lw', 'bl') + " " + make_colors(url, 'y'))
        debug(CONFIGFILE = CONFIG.filename())
        from mega import Mega
        mm = Mega()
        mega_username = CONFIG.get_config('mega.nz', 'username')
        debug(mega_username = mega_username)
        mega_password = CONFIG.get_config('mega.nz', 'password')
        debug(mega_password = mega_password)

        m = mm.login(mega_username, mega_password)
        url_download = m.get_download_url(url)
        debug(url_download = url_download)

    elif 'files.im' in urlparse(url).netloc:
        try:
            from filesim import Filesim
            debug(url = url)
            url_download = Filesim.generate(url)
            debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True

    elif 'justpaste' in urlparse(url).netloc:
        try:
            from justpaste import Justpaste
            url_download = Justpaste.navigator(url)
            if url_download:
                return downloader(url_download, download_path0, saveas, confirm, ext)

        except:
            traceback.format_exc()
            error = True

    elif 'kraken' in urlparse(url).netloc:
        try:
            from kraken import Kraken
            url_download = Kraken.generate(url)
            debug(url_download = url_download)
            url_download = url_download.get('url')
            debug(url_download = url_download)
        except:
            print("ERROR [kraken]:", traceback.format_exc())
            error = True

    elif  '/utils/player/mega/?id' in url:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Cookie': '_as_ipin_ct=ID', 'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Te': 'trailers'}
        headers = Parserheader(header)()
        url = requests.get(url, headers = headers)
        url_download = url.url
        debug(url_download = url_download)
        clipboard.copy(url_download)
        return url_download

    elif 'racaty' in urlparse(url).netloc:
        try:
            from racaty import racaty
            url_download = racaty.racaty(url)
            debug(url_download = url_download)
        except:
            print("ERROR [racaty]:", traceback.format_exc())
            error = True

    elif 'hxfile' in urlparse(url).netloc:
        try:
            from hxfile import Hxfile
            url_download = Hxfile.generate(url)
            debug(url_download = url_download)
            if not url:
                error = True
        except:
            print("ERROR [racaty]:", traceback.format_exc())
            error = True

    elif urlparse(url).netloc == "drive.google.com":
        if urlparse(url).query:
            if "id=" == urlparse(url).query[:3]:
                url_download = url
            else:
                error = True

    elif 'uptobox' in urlparse(url).netloc:
        try:
            from uptobox import Uptobox
            url_download = Uptobox.get_download_link(url)
            print(make_colors("DOWNLOAD URL (uptobox) :", 'b', 'g')  + " " + make_colors(url_download, 'b', 'g'))
        except:
            traceback.format_exc()
            error = True

    elif 'mir.cr' in urlparse(url).netloc or 'mirrored' in urlparse(url).netloc:
        try:
            from mirrored import Mirrored
            url_download = Mirrored.navigator(url)
            debug(url_download = url_download)
            return downloader(url_download, download_path0, saveas0, confirm, ext)
        except:
            print(make_colors("ERROR [mirror/mir.cr]", 'lw', 'r') + " " + make_colors(traceback.format_exc(), 'ly'))
            error = True

    elif 'clicknupload' in urlparse(url).netloc:
        try:
            from clicknupload import Clicknupload
            url_download = Clicknupload.main(url)
            debug(url_download = url_download)
            # return downloader(url_download, download_path0, saveas0, confirm, ext)
        except:
            traceback.format_exc()
            error = True

    elif 'zippyshare' in urlparse(url).netloc:
        print(make_colors("Zippyshare is down Now !", 'lw', 'r'))
        error = True

    elif 'pixeldrain' in urlparse(url).netloc:
        try:
            import pixeldrain
            g = pixeldrain.Pixeldrain()
            url_download = g.generate(url, download_path = download_path, saveas = saveas)
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True

    elif 'qiwi' in urlparse(url).netloc:
        logger("[qiwi] generate {}".format(url))
        try:
            from qiwi import Qiwi
            url_download = Qiwi.generator(url)
            logger("[qiwi] generate {} --> {}".format(url, url_download))
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True
            logger("[qiwi] generate error {} --> {}".format(url, url_download), 'error')
            logger("[qiwi] generate error {} --> {} --> {}".format(url, url_download, traceback.format_exc()), 'error')

    elif 'gofile' in urlparse(url).netloc:
        logger("[GoFile] generate {}".format(url))
        try:
            from gofiledm import GoFile
            url_download, GOFILE_TOKEN = GoFile.generate(url)
            logger("[GoFile] generate {} --> {}".format(url, url_download))
            if len(url_download) > 1:
                ng = 1
                for gofile_link in url_download:
                    print(make_colors(str(ng) + ".", 'lc') + " " + make_colors(gofile_link, 'ly'))
                    ng += 1
                qg = input(make_colors("Select number of link/url:", 'lw', 'bl') + " ")
                if qg:
                    if str(qg).isdigit():
                        if int(qg) <= len(url_download):
                            url_download = url_download[int(qg) - 1]
            else:
                url_download = url_download[0]
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True
            logger("[GoFile] generate error {} --> {}".format(url, url_download), 'error')        

    elif 'wibu' in urlparse(url).netloc:
        try:
            from wibu import Wibu
            url_download = Wibu.generator(url)
            if not url_download:
                print(make_colors("Wibu generator Failed !", 'lw', 'r'))
                error = True
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True

    elif 'mp4upload' in urlparse(url).netloc:
        try:
            import mp4upload
            url_download = mp4upload.Mp4upload.generate(url)
            debug(url_download = url_download, debug = 1)
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True        

    elif 'anonfile' in urlparse(url).netloc or 'bayfiles' in urlparse(url).netloc:
        #try:
            #from anonfile import Anonfile
            #a = Anonfile()
            #url_download = a.generate(url)
            #debug(url_download = url_download)
            #if not url_download:
                #error = True
        #except:
            #traceback.format_exc()
            #error = True
        print(make_colors("Anonfile is down Now !", 'lw', 'r'))
        error = True        

    elif 'mediafire' in urlparse(url).netloc:
        try:
            from mediafire import mediafire
            a = mediafire.Mediafire()
            url_download = a.generate(url)
            debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True


    debug(error = error)

    if error:
        logger("downloader: error: {}".format(url), "error")
        try:
            clipboard.copy(url)
            logger("downloader: error: {} --> clipboard".format(url), "error")
        except:
            pass
        print(make_colors("[ERROR] Get download link", 'lw', 'r') + ", " + make_colors("copy URL to clipboard", 'y'))
    else:

        file_name, ext1 = get_name(url_download)
        if ext1: ext = ext1
        debug(copyurl_only = copyurl_only)

        if copyurl_only:
            if url_download:
                print(make_colors("Url Download:", 'lw', 'lr') + " " + make_colors(url_download, 'y'))
                clipboard.copy(url_download)

                logger("downloader: {} --> clipboard".format(unidecode(url_download)), "debug")
                notify(title="Anoboy", app="anoboy", event="copy to clipboard", message="downloader: {} --> clipboard".format(unidecode(url_download)), icon = str(Path(__file__).parent / Path('logo.png')))
                return url_download
            else:
                print(make_colors("URL:", 'lw', 'lr') + " " + make_colors(url, 'y'))
                clipboard.copy(url)
                logger("downloader: {} --> clipboard".format(url), "notice")
                return url
        if not saveas and name:
            saveas = name
        if not ext and name:
            try:
                if len(os.path.splitext(name)) > 1:
                    ext = os.path.splitext(name)[1]
                    if saveas:
                        saveas = saveas + ext
                        debug(saveas = saveas)
            except:
                pass
        debug(url_download = url_download)
        if not url_download:
            url_download = url
            #clipboard.copy(url)
            #return url
        if not ext and not name:
            debug(url_download = url_download)
            debug(split_url_download = os.path.split(url_download))
            debug(split_ext = os.path.splitext(os.path.split(url_download)[-1]))
            ext = os.path.splitext(os.path.split(url_download)[-1])[1]#.lower()
            debug(ext = ext)
            if ext in [".mp4", ".mkv", ".avi"]:
                name = os.path.split(url_download)[-1]
                debug(name = name)
        if not ext or ext.strip() == '':
            ext = ".mp4"
        if ext and saveas:
            debug(saveas = saveas)
            debug(saveas_check = all(iext in saveas.lower() for iext in [".mp4", ".mkv", ".avi"]))
            if not list(filter(lambda k: saveas.endswith(k), [".mp4", ".mkv", ".avi"])):
                saveas = saveas + str(ext).lower()
                debug(saveas = saveas)
        debug(ext = ext)
        debug(saveas = saveas)
        if nodownload:
            if url_download:
                return url_download, saveas
            else:
                return '', ''
        print(make_colors("SAVEAS:", 'lw', 'bl') + " " + make_colors(saveas, 'lw', 'r'))
        debug(url_download = url_download)
        debug(download_path = download_path)
        if saveas:
            while 1:
                if saveas[-1] == ".":
                    saveas = saveas[:-1]
                else:
                    break
        debug(saveas = saveas)

        if saveas and ext1:
            if not list(filter(lambda k: saveas.endswith(k), [".mp4", ".mkv", ".avi"])):
                saveas = saveas + ext1
                debug(saveas = saveas)  
        elif saveas:
            if not list(filter(lambda k: saveas.endswith(k), [".mp4", ".mkv", ".avi"])):
                saveas = saveas + ".mp4"
                debug(saveas = saveas)

        debug(saveas = saveas)

        if sys.platform == 'win32':
            #sys.exit()
            logger("downloader [win32]: downloading: {} --> {} --> {}".format(url, url_download, saveas))
            if 'gofile' in urlparse(url).netloc:
                d.download(url_download, download_path, saveas, confirm = confirm, cookie = {
                    'accountToken': GOFILE_TOKEN,
                    }, postData = {
                        'authorization': 'Bearer ' + GOFILE_TOKEN,
                    'cookie': 'accountToken=' + GOFILE_TOKEN,
                    })
            else:
                d.download(url_download, download_path, saveas, confirm = confirm)
            logger("downloader [win32]: finish: {} --> {} --> {}".format(url, url_download, saveas))
            if thumb:
                thumb_name = os.path.splitext(saveas)[0]
                if not os.path.isfile(os.path.join(os.path.dirname(download_path), os.path.basename(thumb_name)) + ".jpg"):
                    d.download(thumb, os.path.dirname(download_path), os.path.basename(thumb_name) + ".jpg", confirm = confirm)

        else:
            logger("downloader [linux]: downloading: {} --> {} --> {}".format(unidecode(url), unidecode(url_download), unidecode(saveas)))
            debug(saveas = saveas)
            #pause()
            download_linux(url_download, download_path, saveas, cookies = {'accountToken': GOFILE_TOKEN,}, headers = {
                'authorization': 'Bearer ' + GOFILE_TOKEN,
                'cookie': 'accountToken=' + GOFILE_TOKEN,
            })
            logger("downloader [linux]: finish: {} --> {} --> {}".format(unidecode(url), unidecode(url_download), unidecode(saveas)))
            if thumb:
                thumb_name = os.path.splitext(saveas)[0]
                if not os.path.isfile(os.path.join(os.path.dirname(download_path), os.path.basename(thumb_name)) + ".jpg"):
                    download_linux(thumb, os.path.dirname(download_path), os.path.basename(thumb_name) + ".jpg", cookies, check_file = False)

    icon = None
    if os.path.isfile(os.path.join(os.path.dirname(__file__), 'logo.png')):
        icon = os.path.join(os.path.dirname(__file__), 'logo.png')

    if sys.platform == 'win32':
        notify("Download start: ", saveas, "Anoboy", "downloading", icon = icon)
    else:
        notify("Download finish: ", saveas, "Anoboy", "finish", icon = icon)

    debug(url_download = url_download)
    if url_download:
        return url_download
    return url

def download_linux(url, download_path=os.getcwd(), saveas=None, cookies = {}, downloader = 'wget', check_file = True, headers = None):
    '''
        downloader: aria2c, wget, uget, persepolis
    '''
    if saveas: saveas = re.sub("\.\.", ".", saveas)
    if not download_path or not os.path.isdir(download_path):
        if CONFIG.get_config('DOWNLOAD', 'path', os.getcwd()):
            download_path = CONFIG.get_config('DOWNLOAD', 'path')
    print(make_colors("DOWNLOAD_PATH (linux):", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))
    print(make_colors("DOWNLOAD LINK [direct]:", 'b', 'lc') + " " + make_colors(url, 'b', 'ly'))
    if sys.version_info.major == 3:
        aria2c = os.popen("aria2c")
        wget = os.popen("wget")
        persepolis = os.popen("persepolis --help")
    else:
        aria2c = os.popen3("aria2c")
        wget = os.popen3("wget")
        persepolis = os.popen3("persepolis --help")

    if downloader == 'aria2c' and not re.findall("not found\n", aria2c[2].readlines()[0]):
        if saveas:
            saveas = '-o "{0}"'.format(saveas.encode('utf-8', errors = 'ignore'))
        cmd = 'aria2c -c -d "{0}" "{1}" {2} --file-allocation=none'.format(os.path.abspath(download_path), url, saveas)
        os.system(cmd)
        logger(cmd)
    elif downloader == 'wget':
        if sys.version_info.major == 2:
            if re.findall("not found\n", wget[2].readlines()[0]):
                print(make_colors("Download Failed !", 'lw', 'r'))
                return False
        filename = ''
        if saveas:
            if sys.version_info.major == 3:
                filename = os.path.join(os.path.abspath(download_path), saveas)
                saveas = ' -O "{}"'.format(os.path.join(os.path.abspath(download_path), saveas))
            else:
                filename = os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore'))
                saveas = ' -O "{}"'.format(os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore')))
        else:
            saveas = '-P "{0}"'.format(os.path.abspath(download_path))
            filename = os.path.join(os.path.abspath(download_path), os.path.basename(url))
        headers_add = ''
        header_cookie = ""
        if cookies:
            for i in cookies: header_cookie +=str(i) + "= " + cookies.get(i) + "; "
            headers_add = ' --header="Cookie: ' + header_cookie[:-2] + '"' +\
                ' --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"' +\
                ' --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"' +\
                ' --header="Sec-Fetch-Site: same-origin" --header="Accept-Encoding: gzip, deflate, br" --header="Connection: keep-alive"' +\
                ' --header="Upgrade-Insecure-Requests: 1"' +\
                ' --header="Sec-Fetch-Mode: navigate"' +\
                ' --header="Sec-Fetch-User: ?1"' +\
                ' --header="Sec-Fetch-Dest: document"'
        debug(headers = headers)
        headers = headers_add + " ".join([' --header="' + i + ": " + headers.get(i) + '"' for i in headers])
        debug(headers = headers)
        cmd = 'wget -c "' + url + '" {}'.format(unidecode(saveas)) + headers

        if 'racaty' in url: cmd+= ' --no-check-certificate'
        print(make_colors("CMD:", 'lw', 'lr') + " " + make_colors(cmd, 'lw', 'r'))
        a = os.system(cmd)
        logger(cmd)
        if a:
            logger("It's seem error while downloading: {}".format(url), 'error')
        if CONFIG.get_config('policy', 'size'):
            size = ''
            try:
                size = bitmath.parse_string_unsafe(CONFIG.get_config('policy', 'size'))
            except ValueError as e:
                logger(str(e), 'error')
            if check_file:
                if size and not bitmath.getsize(filename).MB.value > size.value:
                    print(make_colors("REMOVE FILE", 'lw', 'r') + " [" + make_colors(bitmath.getsize(filename).kB) + "]: " + make_colors(filename, 'y') + " ...")
                    os.remove(filename)
                    logger("File not qualify of size policy", 'critical')

    elif downloader == 'persepolis'  and not re.findall("not found\n", persepolis[2].readlines()[0]):
        cmd = 'persepolis --link "{0}"'.format(url)
        a = os.system(cmd)
        if a:
            logger("It's seem error while downloading: {}".format(url), 'error')
        logger(cmd)
    else:
        try:
            from pywget import wget as d
            d.download(url, download_path, saveas.decode('utf-8', errors = 'ignore'))
            logger("download: {} --> {}".format(url, os.path.join(download_path, saveas.decode('utf-8', errors = 'ignore'))))
        except Exception as e:
            print(make_colors("Can't Download this file !, no Downloader supported !", 'lw', 'lr', ['blink']))
            clipboard.copy(url)
            logger("download: copy '{}' --> clipboard".format(url), "error")
            logger(str(e), 'error')



