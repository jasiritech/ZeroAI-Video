"""
engine/subtitles.py
Generates stylish TikTok/Alex Hormozi style animated ASS subtitles with word-by-word highlights.
Supports exact boundary markers or proportional rhythmic speech timing.
"""

import os
import re
from typing import List, Dict, Any, Optional

def format_timestamp(seconds: float) -> str:
    """Converts seconds into ASS timestamp format: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    csecs = int(round((seconds - int(seconds)) * 100))
    if csecs >= 100:
        secs += 1
        csecs = 0
    return f"{hrs}:{mins:02d}:{secs:02d}.{csecs:02d}"

def build_proportional_word_timings(text: str, duration: float) -> List[Dict[str, Any]]:
    """
    Rhythmically assigns timestamps to words across speech duration.
    Leaves 0.5s padding at start and 1.0s at end.
    """
    words = [w.strip() for w in re.split(r'\s+', text) if w.strip()]
    if not words:
        return []

    start_pad = 0.4
    speech_duration = max(2.0, duration - 1.2)
    time_per_word = speech_duration / len(words)

    words_data = []
    for idx, w in enumerate(words):
        t = start_pad + (idx * time_per_word)
        words_data.append({"word": w, "start": round(t, 2)})

    return words_data

def generate_animated_ass(
    words_data: List[Dict[str, Any]],
    output_ass_path: str,
    video_width: int = 1080,
    video_height: int = 1920,
    raw_text: Optional[str] = None,
    total_duration: float = 10.0,
    words_per_group: int = 4
) -> str:
    """
    Groups words into short readable clusters (e.g. 3-4 words) and generates ASS dialogue events
    where each active word lights up in vibrant golden-yellow with an outline.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)
    
    font_size = 68 if video_height > 1200 else 44
    margin_v = 420 if video_height > 1200 else 110

    # If no word boundaries captured, build proportional timings
    if (not words_data or len(words_data) == 0) and raw_text:
        words_data = build_proportional_word_timings(raw_text, total_duration)
    
    # ASS Header
    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTokActive,Segoe UI Black,{font_size},&H0000FFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,40,40,{margin_v},1
Style: TikTokDim,Segoe UI Black,{font_size},&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    if not words_data:
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
        return output_ass_path

    # Group words into chunks of 3-4 words for high retention
    chunks = []
    current_chunk = []
    for item in words_data:
        current_chunk.append(item)
        if len(current_chunk) >= words_per_group:
            chunks.append(current_chunk)
            current_chunk = []
    if current_chunk:
        chunks.append(current_chunk)

    dialogues = []
    for chunk in chunks:
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["start"] + 0.8
        
        for idx, active_item in enumerate(chunk):
            w_start = active_item["start"]
            if idx + 1 < len(chunk):
                w_end = chunk[idx + 1]["start"]
            else:
                w_end = chunk_end
                
            if w_end <= w_start:
                w_end = w_start + 0.35

            # Build line where active word has vibrant color &H0000FFFF (Yellow in BGR)
            line_parts = []
            for j, word_item in enumerate(chunk):
                raw_word = word_item["word"].upper()
                if j == idx:
                    line_parts.append(f"{{\\c&H0000FFFF\\fscx108\\fscy108}}{raw_word}{{\\r}}")
                else:
                    line_parts.append(f"{{\\c&H00FFFFFF}}{raw_word}{{\\r}}")

            full_line_text = " ".join(line_parts)
            dialogue_str = (
                f"Dialogue: 0,{format_timestamp(w_start)},{format_timestamp(w_end)},"
                f"TikTokActive,,0,0,0,,{full_line_text}\n"
            )
            dialogues.append(dialogue_str)

    ass_content += "".join(dialogues)

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    return output_ass_path
