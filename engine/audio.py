"""
engine/audio.py
Audio synthesis and mixing engine using Windows offline SAPI TTS and FFmpeg.
Generates speech narration with word-level boundary data, ambient soundtrack, and SFX.
"""

import os
import json
import subprocess
from typing import Optional, List, Dict, Any, Tuple

def get_audio_duration(audio_path: str) -> float:
    """Uses ffprobe to obtain exact audio duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        print(f"[Audio] ffprobe duration error for {audio_path}: {e}")
        return 10.0

def generate_tts_with_timestamps(
    text: str,
    output_path: str,
    voice_gender: str = "Female",
    rate: int = 0
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Generates offline speech audio using Windows System.Speech.
    Captures word-by-word timestamps via SpeakProgress event.
    Returns: (output_wav_path, list_of_word_events)
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    work_dir = os.path.dirname(os.path.abspath(output_path))
    
    safe_text = text.replace('"', '`"').replace("'", "''")
    gender_enum = "Female" if voice_gender.lower() == "female" else "Male"
    words_json_file = os.path.join(work_dir, "temp_words.json")

    ps_content = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::{gender_enum})
$synth.Rate = {rate}
$synth.SetOutputToWaveFile('{os.path.abspath(output_path)}')

$words = New-Object System.Collections.ArrayList
$synth.add_SpeakProgress({{
    param($s, $e)
    $words.Add([PSCustomObject]@{{
        word = $e.Text
        start = [math]::Round($e.AudioPosition.TotalSeconds, 2)
    }}) | Out-Null
}})

$synth.Speak('{safe_text}')
$synth.Dispose()

$words | ConvertTo-Json | Out-File -FilePath '{os.path.abspath(words_json_file)}' -Encoding utf8
"""
    temp_ps_file = os.path.join(work_dir, "temp_tts.ps1")
    with open(temp_ps_file, "w", encoding="utf-8") as f:
        f.write(ps_content)

    words_data = []
    try:
        res = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", temp_ps_file],
            capture_output=True,
            text=True
        )
        if os.path.exists(temp_ps_file):
            os.remove(temp_ps_file)

        if os.path.exists(words_json_file):
            try:
                with open(words_json_file, "r", encoding="utf-8") as jf:
                    loaded = json.load(jf)
                    if isinstance(loaded, dict):
                        words_data = [loaded]
                    elif isinstance(loaded, list):
                        words_data = loaded
            except Exception:
                pass
            os.remove(words_json_file)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[Audio] TTS generated: {output_path} ({len(words_data)} word markers)")
            return output_path, words_data
        else:
            print(f"[Audio] TTS failed: {res.stderr}")
            return None, []
    except Exception as e:
        print(f"[Audio] TTS execution error: {e}")
        if os.path.exists(temp_ps_file):
            os.remove(temp_ps_file)
        return None, []

def generate_ambient_soundtrack(duration: float, output_path: str) -> str:
    """
    Synthesizes a warm, cinematic ambient background soundtrack using FFmpeg harmonic audio filters.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    chord_expr = (
        "0.15*sin(2*PI*130.81*t) + "
        "0.11*sin(2*PI*164.81*t) + "
        "0.10*sin(2*PI*196.00*t) + "
        "0.07*sin(2*PI*246.94*t) + "
        "0.05*sin(2*PI*293.66*t)"
    )
    
    fade_out_start = max(0.5, duration - 1.5)
    af_filters = (
        f"lowpass=f=850,"
        f"flanger=speed=0.25:depth=3:phase=25,"
        f"tremolo=f=0.5:d=0.3,"
        f"volume=0.8,"
        f"afade=t=in:ss=0:d=1.2,"
        f"afade=t=out:st={fade_out_start}:d=1.5"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"aevalsrc=exprs='{chord_expr}':s=44100:d={duration}",
        "-af", af_filters,
        "-c:a", "pcm_s16le",
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path

def create_complete_audio_track(
    narration_text: Optional[str],
    total_duration: float,
    output_path: str,
    custom_music_path: Optional[str] = None
) -> Tuple[str, float, List[Dict[str, Any]]]:
    """
    Builds the master audio soundtrack:
    1. Generates TTS speech + word timestamps.
    2. Builds ambient music.
    3. Mixes both with audio ducking.
    Returns (master_audio_path, effective_duration, words_data).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    work_dir = os.path.dirname(os.path.abspath(output_path))
    
    voice_file = None
    voice_duration = 0.0
    words_data = []

    if narration_text and narration_text.strip():
        voice_path = os.path.join(work_dir, "temp_narration.wav")
        voice_file, words_data = generate_tts_with_timestamps(narration_text, voice_path, voice_gender="Female")
        if voice_file:
            voice_duration = get_audio_duration(voice_file)
            total_duration = max(total_duration, voice_duration + 2.5)

    music_path = os.path.join(work_dir, "temp_music.wav")
    if custom_music_path and os.path.exists(custom_music_path):
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", custom_music_path,
            "-t", str(total_duration),
            "-af", f"afade=t=in:ss=0:d=1,afade=t=out:st={max(0.5, total_duration - 1.5)}:d=1.5",
            music_path
        ]
        subprocess.run(cmd, capture_output=True, text=True)
    else:
        generate_ambient_soundtrack(total_duration, music_path)

    if voice_file and os.path.exists(voice_file):
        filter_complex = (
            "[0:a]volume=1.0[v];"
            "[1:a]volume=0.18[m];"
            "[v][m]amix=inputs=2:duration=longest:dropout_transition=2[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", voice_file,
            "-i", music_path,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", music_path,
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

    final_duration = get_audio_duration(output_path)
    return output_path, final_duration, words_data
