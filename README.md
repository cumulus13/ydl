# ydl

    Download Video and all of video on playlist from Youtube URL

## requirements

* Python > 2.7
* Internet Connection


## install

extract file ydl*-*.zip or ydl*-*.tgz

```bash:

    unzip ydl*.zip
````

change to ydl directory then run:

```python:
    
    python setup.py install
```

after installed successfull, open terminal or console and run:

```bash:
    
    ydl URL -p DIR_SAVE_TO
```

all command help can access by:

```bash:

    yld --help
```

## as module

```python:

>> from ydl import ydl
>> url = "https://www.youtube.com/watch?v=c__fxPkCSns"
>> videos = ydl.get_videos(url)
>> #get all mp4 formats 720
>> videos[0].get('downloads').get('720').get('mp4')
>> #get all webm formats 480
>> videos[0].get('downloads').get('480').get('webm')
>> #support webm and mp4 
```
## How To Use as command line
Watch This Tutorial : [Click Here](https://www.youtube.com/watch?v=c__fxPkCSns)

## authors
[L1cf4ce](licface@yahoo.com)


