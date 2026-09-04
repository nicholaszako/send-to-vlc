from flask import Flask, request
import subprocess
import validators
from urllib.parse import urlsplit, parse_qs

MAX_HEIGHT = 1080
YOUTUBE_DOMAINS = ['youtu.be', 'youtube.com']  # Expand as needed. See https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
ALWAYS_NEW_VLC = True # Whether to kill all VLC instances before attempting to play new media. Generally less buggy this way.

app = Flask(__name__, static_url_path='/static')

# POST request. Supports query parameters such as 't' (time) in URL.
@app.route("/api/send", methods=['POST'])
def stream():
    url = request.form['url']
    if (validators.url(url)):
        vlc_play(url)
        return 'OK', 200
    return 'Bad Request', 400

# Basic GET. Legacy.
@app.route("/api/send-get", methods=['GET'])
def stream_get():
    url = request.args.get('url', '')
    if (validators.url(url)):
        vlc_play(url)
        return 'OK', 200
    return 'Bad Request', 400

# Get URL for best quality (up to max height) audiovideo format
def get_av_url(url: str) -> str:
    ytdlp_cmd = ['yt-dlp', url, '--get-url', '--format', f'best[height<={MAX_HEIGHT}]']
    p = subprocess.run(ytdlp_cmd, check=True, capture_output=True, text=True)
    return p.stdout.strip()

# Get URL for best quality audio-only format
def get_audio_url(url: str) -> str:
    ytdlp_cmd = ['yt-dlp', url, '--get-url', '--format', f'bestaudio']
    p = subprocess.run(ytdlp_cmd, check=True, capture_output=True, text=True)
    return p.stdout.strip()

# Get URL for best quality video-only format
def get_video_url(url: str) -> str:
    ytdlp_cmd = ['yt-dlp', url, '--get-url', '--format', f'bestvideo[height<={MAX_HEIGHT}]']
    p = subprocess.run(ytdlp_cmd, check=True, capture_output=True, text=True)
    return p.stdout.strip()

def vlc_play(uri: str):
    audio_uri = None
    time = None

    if (validators.url(uri)):
        playback_uri = uri
        split_url = urlsplit(uri)
        qs = parse_qs(split_url.query)
        domain = split_url.netloc
        if (domain.startswith('www.')):
            domain = domain[4:]
        if (domain in YOUTUBE_DOMAINS):
            # For YouTube, better luck searching for seperate streams
            playback_uri = get_video_url(uri)
            audio_uri = get_audio_url(uri)
            if (qs.get('t')):
                time = qs['t'][0]

    vlc_cmd = ['vlc', playback_uri, '-f']
    
    if (time):
        vlc_cmd.extend(['--start-time', str(time)])

    if (audio_uri):
        # https://superuser.com/a/691274
        vlc_cmd.extend(['--input-slave', str(audio_uri)])
    
    if (ALWAYS_NEW_VLC):
        subprocess.run(['killall', 'vlc'])

    # Detached process lets VLC do its thing seperately
    subprocess.Popen(vlc_cmd, 
        stdin=subprocess.DEVNULL, 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)