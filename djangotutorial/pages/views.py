from django.shortcuts import render
from django.http import HttpResponse
from yt_dlp import YoutubeDL, utils

# Create your views here.


def home_view(request, *args, **kwargs):
    return render(request, "pages/index.html", {})

# Create your views here.


def url_view(request, *args, **kwargs):
    url = request.POST['url']
    ydl_opts = {
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(info.get('title'))
        '''infoFile = open("info.json", "w")
        infoFile.write(str(info.get('formats')))
        infoFile.close()'''
        formats = info.get('formats')
        audio = ""
        videos = []
        for format in formats:
            new_format = [format.get('ext'),
                          format.get('filesize'),
                          utils.format_bytes(format.get('filesize') if format.get('filesize') is not None else format.get('filesize_approx')),
                          format.get('url'),
                          format.get('acodec'),
                          format.get('vcodec'),
                          format.get('resolution'),
                          format.get('height')]
            if format.get('ext') == 'm4a':
                audio = new_format
            if format.get('ext') == 'mp4' and format.get('vcodec').find("audio") == -1:
                videos.append(new_format)

        print(audio)
        print(videos)
    return render(request, "pages/result.html", {"info": info})
