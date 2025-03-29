from django.shortcuts import render
from django.http import HttpResponse
from yt_dlp import YoutubeDL, utils
from .models import Video
from django.conf import settings
import validators
import json
# Create your views here.


def home_view(request, *args, **kwargs):
    url = request.GET.get('url', "")
    # Lấy tất cả video từ cơ sở dữ liệu
    videos = Video.objects.all()

    # Lấy 5 video cuối cùng
    last_5_videos = videos.order_by('-id')[:5]

    return render(request, "pages/index.html", {"videos": last_5_videos, "url" : url})

# Create your views here.
def download_url(request, *args, **kwargs):
    url = request.POST['url']
    format = request.POST['format']
    ydl_opts = {
        'format': format,
        'outtmpl': settings.VIDEO_PATH + '/static/videos/%(title)s_%(format)s.mp4',
        'get-filename': True,
    }
    file_path = ""
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        file_path = ydl.prepare_filename(info).replace(settings.VIDEO_PATH, "")
        ydl.process_info(info)  # starts the download
    
    response_data = {
        'message': 'Video downloaded successfully!',
        'url': file_path,
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

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
            heights = {}
            for format in formats:
                new_format = [format.get('ext'),
                              format.get('filesize'),
                              utils.format_bytes(format.get('filesize') if format.get(
                                  'filesize') is not None else format.get('filesize_approx')),
                              format.get('url'),
                              format.get('acodec'),
                              format.get('vcodec'),
                              format.get('resolution'),
                              format.get('height'),
                              format.get('format_id'),]
                if format.get('ext') == 'm4a':
                    audio = new_format
                if format.get('ext') == 'mp4' and format.get('resolution').find("audio") == -1:
                    if format.get('height'):
                        heights[format.get('height')] = 1
                if format.get('ext') == 'mp4' and format.get('resolution').find("audio") == -1 and format.get("url").find("manifest") == -1:
                    print(format.get('acodec'))
                    if format.get('acodec') != "none":
                        video = new_format
                    else:
                        list_video = videos.get(format.get('height'), [])
                        list_video.append(new_format)
                        videos[format.get('height')] = list_video
            updated_info.append((info, audio, video, videos, heights))

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