from django.shortcuts import render
from django.http import HttpResponse
from yt_dlp import YoutubeDL, utils
from .models import Video
import validators
# Create your views here.


def home_view(request, *args, **kwargs):
    url = request.GET.get('url', "")
    # Lấy tất cả video từ cơ sở dữ liệu
    videos = Video.objects.all()

    # Lấy 5 video cuối cùng
    last_5_videos = videos.order_by('-id')[:5]

    return render(request, "pages/index.html", {"videos": last_5_videos, "url" : url})

# Create your views here.


def url_view(request, *args, **kwargs):
    url = request.POST['url']
    ydl_opts = {
    }

    with YoutubeDL(ydl_opts) as ydl:
        if validators.url(url):
            info_videos = [ydl.extract_info(url, download=False)]
        else:
            info_videos = ydl.extract_info(
                f"ytsearch:{url}", download=False).get('entries')

        updated_info = []
        for info in info_videos:
            formats = info.get('formats')
            audio = []
            video = {}
            videos = {}
            for format in formats:
                new_format = [format.get('ext'),
                              format.get('filesize'),
                              utils.format_bytes(format.get('filesize') if format.get(
                                  'filesize') is not None else format.get('filesize_approx')),
                              format.get('url'),
                              format.get('acodec'),
                              format.get('vcodec'),
                              format.get('resolution'),
                              format.get('height')]
                if format.get('ext') == 'm4a':
                    audio = new_format
                if format.get('ext') == 'mp4' and format.get('resolution').find("audio") == -1 and format.get("url").find("manifest") == -1:
                    print(format.get('acodec'))
                    if format.get('acodec') != "none":
                        print(new_format)
                        video = new_format
                    else:
                        list_video = videos.get(format.get('height'), [])
                        list_video.append(new_format)
                        videos[format.get('height')] = list_video
            updated_info.append((info, audio, video, videos))

        # add into db
        info = updated_info[0][0]
        # check id video exist
        if not Video.objects.filter(videoId=info.get('id')).exists():
            video_obj = Video(videoId=info.get('id'),
                                link=info.get('webpage_url'),
                                title=info.get('title'),
                                description=info.get('description'),
                                thumbnail=info.get('thumbnail'))
            video_obj.save()

    return render(request, "pages/result.html", {"updated_info": updated_info})
