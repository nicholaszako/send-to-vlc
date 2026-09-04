# send-to-vlc

## Description

send-to-vlc is a bare-bones web app for sending a URL to for streaming by VLC on a remote device. [Yt-dlp](https://github.com/yt-dlp/yt-dlp) is used to get URLs that VLC can actually use for playback. This app was made with the Raspberry Pi 5 in mind as video streaming seems to be far more performant through VLC compared to other options such as browsers or mpv.

## Requirements
- Python3
    - `flask`
    - `validators`
- VLC
- yt-dlp

## Quick Start

Linux:
```
git clone https://github.com/nicholaszako/send-to-vlc.git
cd ./send-to-vlc
python3 -m venv .venv
source .venv/bin/activate
pip install flask validators
python -m main
```
Input page will be available at http://(host IP):8080/static/send.html
