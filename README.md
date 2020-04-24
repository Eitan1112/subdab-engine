# Syncit
The backend for the syncit webapp. Recieves buffers and subtitles and uses it to find the delay and eventually sync it with the video.

## Installation
```
cd /var/www
git clone https://www.github.com/Eitan1112/syncit-backend.git
cd syncit-backend
sudo apt install swig libasound2-dev libpulse-dev
python3 -m pip install -r requirements.txt
python3 -m syncit
```

## Requiremenets
Requirements.txt and PocketSphinx.