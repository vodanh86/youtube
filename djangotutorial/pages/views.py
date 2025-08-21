from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponse
from yt_dlp import YoutubeDL, utils
from .models import Video
from django.conf import settings
import validators
import json
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import requests
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

def extract_videos(info_videos):
    updated_info = []
    for info in info_videos:
        formats = info.get('formats')
        audio = []
        video = {}
        videos = {}
        heights = {}
        for format in formats:
            height = format.get('height')
            if height:
                if height > 100 and height < 200:
                    height = 144
                if height > 200 and height < 300:
                    height = 240
                if height > 300 and height < 400:
                    height = 360
                if height > 400 and height < 500:
                    height = 480
                if height > 500 and height < 800:
                    height = 720
                if height > 800 and height < 1200:
                    height = 1080

            new_format = [format.get('ext'),
                            format.get('filesize'),
                            utils.format_bytes(format.get('filesize') if format.get(
                                'filesize') is not None else format.get('filesize_approx')),
                            format.get('url'),
                            format.get('acodec'),
                            format.get('vcodec'),
                            format.get('resolution'),
                            height,
                            format.get('format_id'),]
            if format.get('ext') == 'm4a':
                audio = new_format
            if format.get('ext') == 'mp4' and format.get('resolution').find("audio") == -1:
                if format.get('height'):
                    heights[height] = 1
            if format.get('ext') == 'mp4' and format.get('resolution').find("audio") == -1 and format.get("url").find("manifest") == -1:
                print(format.get('acodec'))
                if format.get('acodec') != "none":
                    video = new_format
                else:
                    list_video = videos.get(height, [])
                    list_video.append(new_format)
                    videos[height] = list_video
        updated_info.append((info, audio, video, videos, heights))

    return updated_info

def url_view(request, *args, **kwargs):
    url = request.POST['url']
    ydl_opts = {
    }

    with YoutubeDL(ydl_opts) as ydl:
        if validators.url(url):
            info_videos = [ydl.extract_info(url, download=False)]
        else:
            info_videos = ydl.extract_info(
                f"ytsearch5:{url}", download=False).get('entries')
        updated_info = extract_videos(info_videos)
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


def api_search_video(request):
    keyword = request.GET.get('q', '')
    ydl_opts = {'default_search': 'ytsearch5'}
    results = []
    if keyword:
        with YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(f"ytsearch5:{keyword}", download=False)
            print(search_result)
            for entry in search_result.get('entries', []):
                results.append({
                    'id': entry.get('id'),
                    'title': entry.get('title'),
                    'description': entry.get('description'),
                    'thumbnail': entry.get('thumbnail'),
                    'webpage_url': entry.get('webpage_url'),
                })
    return JsonResponse({'results': results})

def api_search_playlist(request):
    keyword = request.GET.get('q', '')
    ydl_opts = {'extract_flat': True, 'default_search': 'ytsearch5'}
    results = []
    if keyword:
        with YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(f"ytsearch5:{keyword} playlist", download=False)
            for entry in search_result.get('entries', []):
                print(entry)    
                if entry.get('_type') == 'playlist':
                    results.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': entry.get('url'),
                        'webpage_url': entry.get('webpage_url'),
                    })
    return JsonResponse({'results': results})

def api_playlist_items(request):
    keyword = request.GET.get('keyword', '')  # dùng param url cho cả url và tên playlist
    results = []
    if keyword:
        try:
            ydl_opts = {'extract_flat': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(keyword, download=False)
                # Nếu là playlist hợp lệ
                if 'entries' in info:
                    for entry in info.get('entries', []):
                        results.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': entry.get('url'),
                            'webpage_url': entry.get('webpage_url'),
                            'duration': entry.get('duration'),
                            'thumbnail': entry.get('thumbnail'),
                        })
                    return JsonResponse({'results': results})
                else:
                    raise Exception("Not a playlist")
        except Exception:
            # Nếu không tìm thấy playlist, trả về danh sách playlist gần giống
            with YoutubeDL({'extract_flat': True, 'default_search': 'ytsearch5'}) as ydl:
                search_result = ydl.extract_info(f"ytsearch5:{keyword} playlist", download=False)
                suggestions = []
                for entry in search_result.get('entries', []):
                    if entry.get('_type') == 'playlist':
                        suggestions.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': entry.get('url'),
                            'webpage_url': entry.get('webpage_url'),
                        })
                return JsonResponse({'error': 'Playlist not found. Here are some suggestions.', 'results': suggestions}, status=404)
    return JsonResponse({'error': 'Invalid keyword or playlist not found'}, status=400)


def api_download_thumbnail(request):
    url = request.GET.get('url', '')
    if url:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return FileResponse(response.raw, content_type='image/jpeg')
    return JsonResponse({'error': 'Invalid URL or download failed'}, status=400)

def api_download_video(request):
    keyword = request.GET.get('keyword', '') 
    ydl_opts = {'default_search': 'ytsearch5'}
    if keyword:
        with YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(f"ytsearch5:{keyword}", download=False).get('entries')
            updated_info = extract_videos(search_result)
            updated_info = [info[3] for info in updated_info]
        return JsonResponse({'results': updated_info})
    return JsonResponse({'error': 'Invalid keyword or no video found'}, status=400)