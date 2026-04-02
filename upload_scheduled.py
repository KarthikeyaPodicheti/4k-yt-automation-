#!/usr/bin/env python3
"""
🎬 4k Edits YouTube Automation
Uploads random videos from Drive to @4keditzzzz-007 YouTube channel
"""

import os
import json
import random
import sys
import pickle
from datetime import datetime, timedelta
from typing import Any, Set, Dict
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Configuration
DRIVE_FOLDER_ID = '1z57u3QvY5BE5uZWQ4UA5x5HPXX0vQ4TE'
PROCESSED_LOG = 'processed_videos.json'
UPLOAD_HISTORY = 'upload_history.json'
DAILY_COUNT = 'daily_upload_count.json'

# YouTube Secrets (From GitHub environment)
TOKEN_BASE64 = os.environ.get('TOKEN_PICKLE_BASE64')
SERVICE_ACCOUNT_BASE64 = os.environ.get('SERVICE_ACCOUNT_BASE64')

# Titles - Hooks for edits
TITLES = [
    "Wait for the beat drop 🤯 4k",
    "Best 4K Edit 🔥 Wait for it",
    "This edit is illegal 🥵 4K",
    "You weren't ready for this 😤",
    "4K Quality at its peak ✨",
    "Watch till the end... pure madness 🤯",
    "They went too hard on this one 🔥",
    "Only true fans will feel this 😱",
    "The transition though... 🥵 4K",
    "Smooth 4K Edit 🔥",
    "Wait for it 🥶 4K",
    "Bro cooked a masterpiece 👨‍🍳🔥",
    "This 4K hits different ✨",
    "Unexpected ending... 😲",
    "The quality is insane! ✨ #shorts",
    "4K Marvel Edit 🔥 #shorts",
    "Neymar Jr 4K flow ⚡",
    "Best car edit of the week? 🏎️",
]

def get_youtube_creds():
    """Load YouTube API credentials from base64 env var"""
    if not TOKEN_BASE64:
        raise ValueError("TOKEN_PICKLE_BASE64 environment variable not set")
    creds_bytes = base64.b64decode(TOKEN_BASE64)
    return pickle.loads(creds_bytes)

def get_drive_creds():
    """Load Drive API credentials from base64 env var"""
    if not SERVICE_ACCOUNT_BASE64:
        raise ValueError("SERVICE_ACCOUNT_BASE64 environment variable not set")
    
    sa_json = json.loads(base64.b64decode(SERVICE_ACCOUNT_BASE64).decode('utf-8'))
    return service_account.Credentials.from_service_account_info(
        sa_json,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )

def get_unprocessed_videos(drive: Any):
    """Get list of videos not yet uploaded"""
    processed = set()
    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, 'r') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    processed = set(str(item) for item in data)
            except json.JSONDecodeError:
                pass
    
    videos = []
    page_token = None
    
    while True:
        response = drive.files().list(
            q=f"'{DRIVE_FOLDER_ID}' in parents and trashed = false",
            fields='nextPageToken, files(id, name, mimeType, shortcutDetails)',
            pageToken=page_token,
            pageSize=100
        ).execute()
        
        for f in response.get('files', []):
            if f['mimeType'] == 'application/vnd.google-apps.shortcut':
                if 'shortcutDetails' in f:
                    real_id = f['shortcutDetails']['targetId']
                    videos.append({'id': f['id'], 'real_id': real_id, 'name': f['name']})
            elif f['mimeType'].startswith('video/'):
                videos.append({'id': f['id'], 'real_id': f['id'], 'name': f['name']})
        
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    unprocessed = [v for v in videos if v['id'] not in processed]
    return unprocessed, processed

def download_video(drive, video_id, name):
    """Download video from Drive to temporary file"""
    clean_name = "".join(c for c in name if c.isalnum() or c in '._-').rstrip()
    if not clean_name.endswith('.mp4'):
        clean_name += '.mp4'
    
    local_path = f"4kedit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{clean_name}"

    request = drive.files().get_media(fileId=video_id)
    
    with open(local_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  ⬇\ufe0f Download: {int(status.progress() * 100)}%")
    
    return local_path

def upload_video():
    """Main upload function"""
    print(f"\n{'='*70}")
    print(f"🎬 4K EDITS YOUTUBE UPLOAD")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*70}\n")
    
    print("[1/5] 🔧 Initializing APIs...")
    youtube_creds = get_youtube_creds()
    youtube = build('youtube', 'v3', credentials=youtube_creds, cache_discovery=False)
    
    drive_creds = get_drive_creds()
    drive = build('drive', 'v3', credentials=drive_creds)
    print("  ✅ APIs ready")
    
    print("\n[2/5] 📁 Checking Drive for 4k edits...")
    unprocessed, processed = get_unprocessed_videos(drive)
    
    if not unprocessed:
        print("  ❌ No unprocessed videos found in Drive folder!")
        return False
    
    print(f"  ✅ {len(unprocessed)} unprocessed videos available")
    
    # Randomly select video
    video = random.choice(unprocessed)
    print(f"\n[3/5] 🎯 Selected: {video['name']}")
    
    print("\n[4/5] ⬇\ufe0f Downloading from Drive...")
    local_path = download_video(drive, video['real_id'], video['name'])
    size_mb = os.path.getsize(local_path) / (1024*1024)
    print(f"  ✅ Downloaded: {size_mb:.1f} MB")
    
    print("\n[5/5] ⬆\ufe0f Uploading to YouTube...")
    
    HASHTAG_SETS = [
        "#4k #shorts #edits #anime",
        "#edit #shorts #4k #marvel",
        "#neymar #shorts #4k #edit",
        "#phonk #cars #4k #shorts",
        "#movies #scenes #4k #edit",
        "#lamborghini #4kedit #shorts",
        "#shorts #status #trending #viral"
    ]
    
    base_title = random.choice(TITLES)
    random_hashtags = random.choice(HASHTAG_SETS)
    
    title = f"{base_title} {random_hashtags}"
    if len(title) > 100:
        title = title[:97] + "..."
    
    print(f"  📝 Generated Title: {title}")
    
    description = f"""{title}

⚡ Welcome to @4keditzzzz-007!
The home of premium 4K quality edits. We drop the hardest edits, phonk vibes, anime flows, marvel scenes, and legendary sports moments!

If you enjoyed this edit, make sure to hit the LIKE button and SUBSCRIBE for daily 4K pure cinema! 🔥🔥

👇 Catch the best edits here 👇
- Anime 4K Edits
- Neymar Jr & Football Magic
- Marvel & Movie Scenes
- Phonk & Luxury Cars (BMW, Lamborghini)

🔔 Turn on notifications to never miss a beat!

#shorts #4k #edits #marvel #anime #neymar #cars #lamborghini #movies #trending #viral

©️ Disclaimer: We do not own any clips or songs used in this video. All credit belongs to the respective owners. This is made purely for entertainment and transformation under fair use.
"""
    
    all_tags = [
        "4k marvel shorts", "shorts", "phonk edits", "lamborghini edit shorts", "edits", 
        "anime shorts", "marvel shorts", "car edits", "anime edits", "neymar edits", "naruto edits", 
        "lamborghini shorts", "neymar clips for edits", "car video edits", "anime 4k edit", 
        "luxury car edits", "indian car edits", "neymar 4k edit", "after effects anime edits", 
        "neymar rare clips for edits", "neymar jr 4k edit", "car edit 4k", "bmw edit 4k", 
        "car music video edits", "neymar 4k edit clip", "how to edit 4k video", 
        "lamborghini edit 4k", "4k marvel edit", "movieclips", "movie", "movies", 
        "snack shack movie", "90s movies", "shortmovie", "stranger things clips", 
        "funny movie scenes", "paramount movies", "paramount movies 2024", "paramount movies digital", 
        "paramount movies to watch", "addams family values full movie", "youtubeshorts", "moviefan", 
        "filmclips", "moviegeek", "moviebuff", "movienight", "moviequotes", "movieaddict", 
        "moviereview", "westernmovies", "disney shows edit", "shortfilm", "shor", "youtubeshort",
        "dad shorts", "funny shorts", "couple shorts", "family shorts", "youtube shorts", 
        "humanity shorts", "sad shorts video", "viral baby shorts", "youtube shorts feed", 
        "popular shorts video", "motivational shorts", "viralshorts"
    ]
    
    clean_all_tags = set(t.replace(".", "").replace(",", "").replace("<", "").replace(">", "").strip() for t in all_tags)
    unique_tags = list(clean_all_tags)
    random.shuffle(unique_tags)
    
    selected_tags = []
    current_length = 0
    
    for tag in unique_tags:
        if not tag:
            continue
        added_len = len(tag) + 1  
        if len(selected_tags) < 15 and current_length + added_len <= 400:
            selected_tags.append(tag)
            current_length += added_len

    # Schedule for +2 hours to allow 4K processing
    publish_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z'

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': selected_tags,
            'categoryId': '24',  # 24 = Entertainment
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': publish_time,
            'madeForKids': False
        }
    }
    
    media = MediaFileUpload(local_path, mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status is not None:
                print(f"  📤 Upload progress: {int(status.progress() * 100)}%")
        except Exception as e:
            print(f"  ⚠️ Error uploading chunk: {e}")
            raise
    
    video_id = response['id']
    
    # Save State
    processed.add(video['id'])
    with open(PROCESSED_LOG, 'w') as f:
        json.dump(list(processed), f)
    
    history = []
    if os.path.exists(UPLOAD_HISTORY):
        with open(UPLOAD_HISTORY, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                pass
    
    history.append({
        'timestamp': datetime.now().isoformat(),
        'title': title,
        'video_id': video_id,
        'drive_file': video['name'],
        'file_size_mb': float(round(float(size_mb), 1))
    })
    
    with open(UPLOAD_HISTORY, 'w') as f:
        json.dump(history, f, indent=2)
    
    today = datetime.now().strftime('%Y-%m-%d')
    daily_count = {'date': today, 'count': 0}
    if os.path.exists(DAILY_COUNT):
        with open(DAILY_COUNT, 'r') as f:
            try:
                loaded_count = json.load(f)
                if isinstance(loaded_count, dict) and loaded_count.get('date') == today:
                    daily_count = loaded_count
            except json.JSONDecodeError:
                pass
    
    daily_count['count'] += 1
    with open(DAILY_COUNT, 'w') as f:
        json.dump(daily_count, f, indent=2)
    
    if os.path.exists(local_path):
        os.remove(local_path)
    
    print(f"\n{'='*70}")
    print(f"🎉 SUCCESS! Video uploaded & scheduled!")
    print(f"📺 Title: {title}")
    print(f"🔗 URL: https://youtu.be/{video_id}")
    print(f"⏰ Going public at: {publish_time}")
    print(f"🎬 Remaining unprocessed videos: {len(unprocessed)-1}")
    print(f"{'='*70}\n")
    
    return True

if __name__ == '__main__':
    try:
        success = upload_video()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
