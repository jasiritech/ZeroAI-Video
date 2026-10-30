"""
engine/fetcher.py
Open-source media scraper using Wikipedia and Wikimedia Commons public APIs.
Fetches high-resolution images and encyclopedic summary text without any API keys.
"""

import os
import re
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Tuple, Optional

USER_AGENT = "ZeroAI-Video/1.0 (https://github.com/jasiritech/ZeroAI-Video; contact@jasiritech.com) Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def clean_html(raw_html: str) -> str:
    """Removes HTML tags and clean up whitespace."""
    clean = re.sub(r'<[^>]+>', '', raw_html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def search_topic_and_summary(topic: str) -> Tuple[str, str]:
    """
    Searches Wikipedia for the best matching article title and plain-text summary.
    Returns: (resolved_title, summary_text)
    """
    headers = {'User-Agent': USER_AGENT}
    
    # 1. Search for best title
    search_url = (
        "https://en.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={urllib.parse.quote(topic)}&utf8=&format=json"
    )
    req = urllib.request.Request(search_url, headers=headers)
    best_title = topic
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('query', {}).get('search', [])
            if results:
                best_title = results[0]['title']
    except Exception as e:
        print(f"[Fetcher] Search error: {e}")

    # 2. Fetch plain text extract (intro) for narration
    extract_url = (
        "https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
        f"&exintro=1&explaintext=1&titles={urllib.parse.quote(best_title)}&format=json"
    )
    req = urllib.request.Request(extract_url, headers=headers)
    summary = ""
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                summary = p.get('extract', '')
                break
    except Exception as e:
        print(f"[Fetcher] Extract error: {e}")

    # Clean up summary
    lines = [l.strip() for l in summary.split("\n") if l.strip()]
    if lines:
        summary = " ".join(lines)
    # Remove citations like [1], [2], etc.
    summary = re.sub(r'\[\d+\]', '', summary)

    return best_title, summary

def fetch_images_for_topic(topic: str, max_images: int = 5, download_dir: str = "downloads") -> List[str]:
    """
    Searches and downloads high-resolution photos for the given topic.
    Returns list of downloaded image file paths.
    """
    os.makedirs(download_dir, exist_ok=True)
    headers = {'User-Agent': USER_AGENT}
    
    best_title, _ = search_topic_and_summary(topic)
    image_candidates = []

    # 1. Get images from the main article
    img_url = (
        "https://en.wikipedia.org/w/api.php?action=query&generator=images"
        f"&titles={urllib.parse.quote(best_title)}&gimlimit=40"
        "&prop=imageinfo&iiprop=url|size|mime&format=json"
    )
    
    try:
        req = urllib.request.Request(img_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                info = p.get('imageinfo', [{}])[0]
                url = info.get('url', '')
                width = info.get('width', 0)
                height = info.get('height', 0)
                mime = info.get('mime', '')
                
                # Filter criteria: valid photo, reasonable dimensions, skip icons/maps/logos
                if ('image/jpeg' in mime or 'image/png' in mime) and width >= 800 and height >= 500:
                    low_url = url.lower()
                    if not any(bad in low_url for bad in ['logo', 'icon', 'symbol', 'flag', 'map', 'chart', 'diagram', 'stub']):
                        image_candidates.append(url)
    except Exception as e:
        print(f"[Fetcher] Article image query error: {e}")

    # 2. If we need more images, perform a direct Wikimedia Commons search
    if len(image_candidates) < max_images:
        commons_url = (
            "https://commons.wikimedia.org/w/api.php?action=query&generator=search"
            f"&gsrnamespace=6&gsrsearch={urllib.parse.quote(topic)}&gsrlimit=20"
            "&prop=imageinfo&iiprop=url|size|mime&format=json"
        )
        try:
            req = urllib.request.Request(commons_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for pid, p in pages.items():
                    info = p.get('imageinfo', [{}])[0]
                    url = info.get('url', '')
                    width = info.get('width', 0)
                    height = info.get('height', 0)
                    mime = info.get('mime', '')
                    if ('image/jpeg' in mime or 'image/png' in mime) and width >= 800 and height >= 500:
                        low_url = url.lower()
                        if not any(bad in low_url for bad in ['logo', 'icon', 'symbol', 'flag', 'map', 'chart', 'diagram', 'stub']):
                            if url not in image_candidates:
                                image_candidates.append(url)
        except Exception as e:
            print(f"[Fetcher] Commons search query error: {e}")

    # 3. Download the top candidates
    downloaded_paths = []
    import time
    for idx, img_url in enumerate(image_candidates):
        if len(downloaded_paths) >= max_images:
            break
        
        ext = ".jpg" if ".png" not in img_url.lower() else ".png"
        filename = f"asset_{idx + 1:02d}{ext}"
        filepath = os.path.join(download_dir, filename)
        
        try:
            print(f"[Fetcher] Downloading ({idx+1}/{max_images}): {img_url[:70]}...")
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp, open(filepath, 'wb') as f:
                f.write(resp.read())
            
            # Verify file size > 20KB
            if os.path.exists(filepath) and os.path.getsize(filepath) > 20000:
                downloaded_paths.append(filepath)
            else:
                if os.path.exists(filepath):
                    os.remove(filepath)
            time.sleep(0.4)
        except Exception as e:
            print(f"[Fetcher] Failed to download {img_url}: {e}")
            time.sleep(0.4)

    return downloaded_paths
