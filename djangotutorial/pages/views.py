from django.shortcuts import render
from django.http import HttpResponse
from yt_dlp import YoutubeDL

# Create your views here.
def home_view(request,*args, **kwargs):
    return render(request, "pages/index.html", {})

# Create your views here.
def url_view(request,*args, **kwargs):
    url = request.POST['url']
    ydl_opts = {
        'playlist_items': '1',
        'extract_flat': 'in_playlist',
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    print(info.get('title'))
    infoFile = open("info.json", "w")
    infoFile.write(str(info))
    infoFile.close()
    return render(request, "pages/result.html", {"info": info})