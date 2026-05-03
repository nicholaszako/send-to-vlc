from flask import Flask, request
import subprocess
import validators
from urllib.parse import urlsplit, parse_qs

MAX_HEIGHT = 1080
GETTABLE_DOMAINS = ['youtu.be', 'youtube.com']  # Expand as needed. See https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
ALWAYS_NEW_VLC = True # Whether to kill all VLC instances before attempting to play new media. Generally less buggy this way.

app = Flask(__name__, static_url_path='/static')

# POST request. Supports query parameters such as 't' (time) in URL.
@app.route("/api/send", methods=['POST'])
def stream():
    if request.method =='POST':
        url = request.form['url']
        if (validators.url(url)):
            playback_url = url
            split_url = urlsplit(url)
            qs = parse_qs(split_url.query)

            time = None
            if (qs.get('t')):
                time = qs['t'][0]

            if (split_url.netloc in GETTABLE_DOMAINS):
                playback_url = get_playback_url(url)
            vlc_play(playback_url, time)
            
            return 'OK', 200
    return 'Bad Request', 400

# Basic GET. Legacy.
@app.route("/api/send-get", methods=['GET'])
def stream_get():
    url = request.args.get('url', '')
    if (validators.url(url)):
        playback_url = url
        
        if (urlsplit(url).netloc in GETTABLE_DOMAINS):
            playback_url = get_playback_url(url)
        vlc_play(playback_url)
        
        return 'OK', 200
    return 'Bad Request', 400

def get_playback_url(url: str) -> str:
    ytdlp_cmd = ['yt-dlp', url, '--get-url', '--format', f'best[height={MAX_HEIGHT}]']
    p = subprocess.run(ytdlp_cmd, check=True, capture_output=True, text=True)
    return p.stdout.strip()

def vlc_play(uri: str, t = None):
    vlc_cmd = ['vlc', uri, '-f']
    
    if (t):
        vlc_cmd.extend(['--start-time', str(t)])
    
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