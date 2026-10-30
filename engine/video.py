"""
engine/video.py
High-performance programmatic video composer using FFmpeg.
Applies Ken Burns camera motion (pan & zoom), typography overlays,
transitions, and audio synchronization.
"""

import os
import subprocess
from typing import List, Dict, Optional, Tuple

RESOLUTIONS = {
    "shorts": (1080, 1920),     # 9:16 Vertical (TikTok, Reels, Shorts)
    "landscape": (1920, 1080),  # 16:9 Horizontal (YouTube, Cinema)
    "square": (1080, 1080)      # 1:1 Square (Instagram Post)
}

FONT_PATH = "C\\:/Windows/Fonts/segoeui.ttf"

def escape_ffmpeg_text(text: str) -> str:
    """Escapes special characters for FFmpeg drawtext filter."""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "'\\''")
    text = text.replace(":", "\\:")
    text = text.replace("%", "\\%")
    text = text.replace(",", "\\,")
    return text

def build_ken_burns_clip(
    image_path: str,
    output_clip_path: str,
    duration: float,
    width: int,
    height: int,
    motion_type: int = 0,
    fps: int = 30
) -> str:
    """
    Renders a single image into an animated video clip with Ken Burns motion.
    motion_type:
      0: Hero Zoom In (1.0 -> 1.25)
      1: Reveal Zoom Out (1.25 -> 1.0)
      2: Pan Left to Right
      3: Pan Right to Left
      4: Upward Pan
    """
    total_frames = int(duration * fps)
    
    # Calculate motion zoom and positioning
    if motion_type == 0:
        # Hero Zoom In
        zoom_expr = "min(zoom+0.0015,1.25)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion_type == 1:
        # Reveal Zoom Out
        zoom_expr = "if(lte(zoom,1.0),1.25,max(1.001,zoom-0.0015))"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion_type == 2:
        # Pan Left to Right
        zoom_expr = "1.15"
        x_expr = f"(on/{total_frames})*(iw-iw/zoom)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion_type == 3:
        # Pan Right to Left
        zoom_expr = "1.15"
        x_expr = f"(1-(on/{total_frames}))*(iw-iw/zoom)"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        # Upward Pan
        zoom_expr = "1.15"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = f"(1-(on/{total_frames}))*(ih-ih/zoom)"

    # Filter pipeline:
    # 1. Scale to cover target frame (force_original_aspect_ratio=increase)
    # 2. Crop to exact target frame aspect ratio
    # 3. Apply zoompan with target resolution
    # 4. setsar=1 to ensure standard square pixel aspect ratio
    # 5. format=yuv420p for universal compatibility
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={width}x{height}:fps={fps},"
        f"setsar=1,"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        output_clip_path
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_clip_path

def compose_final_video(
    image_paths: List[str],
    audio_path: str,
    output_path: str,
    title_text: str = "",
    format_type: str = "shorts",
    total_duration: Optional[float] = None,
    subtitles_ass_path: Optional[str] = None
) -> str:
    """
    Assembles multiple image clips into a unified, cinematic video with audio track,
    title cards, dynamic subtitles, and transitions.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    work_dir = os.path.dirname(os.path.abspath(output_path))
    
    width, height = RESOLUTIONS.get(format_type.lower(), RESOLUTIONS["shorts"])
    
    if total_duration is None:
        from engine.audio import get_audio_duration
        total_duration = get_audio_duration(audio_path)
        
    num_images = max(1, len(image_paths))
    clip_duration = total_duration / num_images
    clip_duration = max(2.5, clip_duration)
    
    print(f"[Video] Rendering {num_images} clips (~{clip_duration:.1f}s each) for {format_type.upper()} ({width}x{height})...")

    rendered_clips = []
    for idx, img_path in enumerate(image_paths):
        clip_path = os.path.join(work_dir, f"temp_clip_{idx:02d}.mp4")
        motion_idx = idx % 5
        print(f"[Video] Animating clip {idx+1}/{num_images} [Motion {motion_idx}]...")
        build_ken_burns_clip(
            image_path=img_path,
            output_clip_path=clip_path,
            duration=clip_duration,
            width=width,
            height=height,
            motion_type=motion_idx
        )
        rendered_clips.append(clip_path)

    # Concat all clips using FFmpeg concat demuxer
    concat_list_file = os.path.join(work_dir, "clips_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for c in rendered_clips:
            safe_clip = os.path.abspath(c).replace("\\", "/")
            f.write(f"file '{safe_clip}'\n")

    unbranded_video = os.path.join(work_dir, "temp_combined_video.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        unbranded_video
    ]
    subprocess.run(concat_cmd, capture_output=True, text=True, check=True)

    # Add Title Badge and Dynamic Subtitles
    print("[Video] Adding title branding, dynamic subtitles & syncing master audio...")
    
    filters = []
    if title_text:
        clean_title = escape_ffmpeg_text(title_text.upper())
        font_size = 52 if format_type == "shorts" else 44
        y_pos = "150" if format_type == "shorts" else "55"
        
        badge_filter = (
            f"drawtext=fontfile='{FONT_PATH}':text='{clean_title}':"
            f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=black@0.65:"
            f"boxborderw=24:x=(w-text_w)/2:y={y_pos}"
        )
        filters.append(badge_filter)

    if subtitles_ass_path and os.path.exists(subtitles_ass_path):
        safe_ass = os.path.abspath(subtitles_ass_path).replace("\\", "/").replace(":", "\\:")
        filters.append(f"ass='{safe_ass}'")

    vf_arg = ",".join(filters) if filters else "null"

    final_cmd = [
        "ffmpeg", "-y",
        "-i", unbranded_video,
        "-i", audio_path,
        "-vf", vf_arg,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    subprocess.run(final_cmd, capture_output=True, text=True, check=True)
    
    # Clean up temp files
    try:
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
        if os.path.exists(unbranded_video):
            os.remove(unbranded_video)
        for c in rendered_clips:
            if os.path.exists(c):
                os.remove(c)
    except Exception:
        pass

    print(f"[Video] Export complete! Saved to: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path
