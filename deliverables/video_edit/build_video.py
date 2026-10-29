import json
import math
import shutil
import subprocess
import textwrap
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'C:\Users\ramuv\AppData\Local\Packages\Microsoft.ScreenSketch_8wekyb3d8bbwe\TempState\Recordings\20261025-1708-14.9934250.mp4')
PLAN = json.loads((ROOT / 'edit_plan.json').read_text())
FPS = 30
BG = '#0b1017'

def run(args):
    subprocess.run(args, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)

def timestamp(t, ass=False):
    if ass:
        n = round(t * 100)
        return f'{n // 360000}:{n // 6000 % 60:02}:{n // 100 % 60:02}.{n % 100:02}'
    n = round(t * 1000)
    return f'{n // 3600000:02}:{n // 60000 % 60:02}:{n // 1000 % 60:02},{n % 1000:03}'

def title_card(filename, kicker, first, second, detail):
    im = Image.new('RGB', (1920, 1080), BG)
    d = ImageDraw.Draw(im)
    regular = r'C:\Windows\Fonts\segoeui.ttf'
    bold = r'C:\Windows\Fonts\segoeuib.ttf'
    d.rounded_rectangle((144, 252, 214, 260), radius=4, fill='#60d5bc')
    d.text((144, 306), kicker, font=ImageFont.truetype(bold, 26), fill='#60d5bc')
    d.text((138, 382), first, font=ImageFont.truetype(bold, 94), fill='#f4f7fb')
    d.text((142, 516), second, font=ImageFont.truetype(regular, 48), fill='#c6d1de')
    d.line((144, 668, 1776, 668), fill='#2a3442', width=2)
    d.text((144, 710), detail, font=ImageFont.truetype(regular, 27), fill='#92a1b4')
    im.save(ROOT / filename)

title_card('intro.png', 'DASHBOARD WALKTHROUGH', 'Loan default risk',
           'Explore the data. Follow the assessment.', 'ANALYTICS   /   ASSESSMENT   /   EXPLAINABILITY')
title_card('outro.png', 'LOAN DEFAULT RISK', 'Understand the estimate.',
           'Review the evidence behind it.', 'Analytical estimates  /  Human review required')

captions = []
chapters = []
timeline = 0.0
all_audio = bytearray()
audio_params = None
script_lines = ['LOAN DEFAULT RISK — VOICEOVER', '',
                'Voice: Microsoft Zira Desktop (locally generated synthetic speech).', '']

for i, chapter in enumerate(PLAN):
    with wave.open(str(ROOT / f'voice_{i:02}_00.wav'), 'rb') as w:
        params = (w.getnchannels(), w.getsampwidth(), w.getframerate())
    if audio_params is None:
        audio_params = params
    assert params == audio_params
    channels, width, rate = params
    bytes_per_sample = channels * width
    def silence(seconds):
        return bytes(round(seconds * rate) * bytes_per_sample)
    audio = bytearray(silence(.35))
    sentence_time = .35
    for j, sentence in enumerate(chapter['sentences']):
        with wave.open(str(ROOT / f'voice_{i:02}_{j:02}.wav'), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == params
            raw = w.readframes(w.getnframes())
            duration = w.getnframes() / rate
        words = sentence.replace('X G Boost', 'XGBoost').split()
        chunks = []
        current = []
        for word in words:
            if current and len(' '.join(current + [word])) > 110:
                chunks.append(current)
                current = []
            current.append(word)
        if current:
            chunks.append(current)
        weight = sum(len(' '.join(chunk)) for chunk in chunks)
        cursor = sentence_time
        for chunk in chunks:
            text = ' '.join(chunk)
            length = duration * len(text) / weight
            captions.append((timeline + cursor, timeline + cursor + length, text))
            cursor += length
        audio.extend(raw)
        sentence_time += duration
        if j < len(chapter['sentences']) - 1:
            audio.extend(silence(.16))
            sentence_time += .16
    audio.extend(silence(.5))
    duration = math.ceil(len(audio) / bytes_per_sample / rate * FPS) / FPS
    desired_bytes = round(duration * rate) * bytes_per_sample
    audio.extend(bytes(desired_bytes - len(audio)))
    all_audio.extend(audio)
    chapters.append({'start': timeline, 'end': timeline + duration,
                     'title': chapter['title'], 'source_clips': chapter['clips']})
    script_lines.extend([f'{timestamp(timeline)} — {chapter["title"]}',
                         ' '.join(chapter['sentences']).replace('X G Boost', 'XGBoost'), ''])
    chapter['duration'] = duration
    timeline += duration

outro_duration = 3.0
all_audio.extend(bytes(round(outro_duration * audio_params[2]) * audio_params[0] * audio_params[1]))
with wave.open(str(ROOT / 'narration_raw.wav'), 'wb') as w:
    w.setnchannels(audio_params[0]); w.setsampwidth(audio_params[1]); w.setframerate(audio_params[2])
    w.writeframes(all_audio)
(ROOT / 'voiceover_script.txt').write_text('\n'.join(script_lines), encoding='utf-8')
(ROOT / 'timeline.json').write_text(json.dumps({'duration': timeline + 3, 'chapters': chapters}, indent=2))

ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1920', 'PlayResY: 1080',
       'WrapStyle: 0', 'ScaledBorderAndShadow: yes', '', '[V4+ Styles]',
       'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
       'Style: Caption,Segoe UI,34,&H00F7F9FC,&H000000FF,&H000B1017,&H000B1017,0,0,0,0,100,100,0,0,1,0,0,2,180,180,10,1',
       'Style: Chapter,Segoe UI Semibold,22,&H00BCD560,&H000000FF,&H000B1017,&H000B1017,-1,0,0,0,100,100,0.6,0,3,8,0,7,100,100,18,1',
       '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
srt = []
for index, (start, end, text) in enumerate(captions, 1):
    lines = textwrap.wrap(text, 58)
    ass_text = r'\N'.join(lines)
    ass.append(f'Dialogue: 1,{timestamp(start,True)},{timestamp(end,True)},Caption,,0,0,0,,{ass_text}')
    srt.extend([str(index), f'{timestamp(start)} --> {timestamp(end)}', '\n'.join(lines), ''])
for index, chapter in enumerate(chapters):
    start = chapter['start'] + (2.0 if index == 0 else 0)
    ass.append(f'Dialogue: 0,{timestamp(start,True)},{timestamp(chapter["end"],True)},Chapter,,0,0,0,,{index+1:02}  /  {chapter["title"].upper()}')
(ROOT / 'captions.ass').write_text('\n'.join(ass), encoding='utf-8')
(ROOT / 'Loan_Risk_Demo.srt').write_text('\n'.join(srt), encoding='utf-8')

for i, chapter in enumerate(PLAN):
    duration = chapter['duration']
    if (ROOT / f'chapter_{i:02}.mp4').exists() and i != 5:
        print(f'Reusing verified chapter {i+1}', flush=True)
        continue
    intro = 2.0 if i == 0 else 0.0
    usable = duration - intro
    source_duration = sum(end - start for start, end in chapter['clips'])
    speed = min(1.7, max(.72, source_duration / usable))
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-filter_complex_threads', '2']
    for start, end in chapter['clips']:
        args += ['-ss', str(start), '-t', str(end - start), '-threads', '2', '-i', str(SOURCE)]
    if intro:
        args += ['-loop', '1', '-framerate', '30', '-i', str(ROOT / 'intro.png')]
    filters = []
    labels = []
    if intro:
        filters.append(f'[{len(chapter["clips"])}:v]trim=duration=2,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[title]')
        labels.append('[title]')
    allocated_frames = 0
    total_frames = round(usable * FPS)
    for j, (start, end) in enumerate(chapter['clips']):
        count = round((end-start) / source_duration * total_frames)
        if j == len(chapter['clips']) - 1:
            count = total_frames - allocated_frames
        allocated_frames += count
        shot_duration = count / FPS
        crop = ''
        if i == 5:
            crop = f'crop=1440:810:410:{220 if j == 0 else 50},'
        filters.append(f'[{j}:v]setpts=(PTS-STARTPTS)/{speed:.8f},fps=30,'
                       f'tpad=stop_mode=clone:stop_duration={duration:.6f},trim=duration={shot_duration:.8f},'
                       f'setpts=PTS-STARTPTS,{crop}scale=1760:990:flags=lanczos,setsar=1,'
                       f'pad=1920:1080:80:0:color={BG},format=yuv420p[v{j}]')
        labels.append(f'[v{j}]')
    filters.append(''.join(labels) + f'concat=n={len(labels)}:v=1:a=0[out]')
    args += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-an', '-t', f'{duration:.8f}',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-threads', '4',
             '-pix_fmt', 'yuv420p', '-r', '30', str(ROOT / f'chapter_{i:02}.mp4')]
    run(args)
    print(f'Rendered {i+1}/{len(PLAN)}: {chapter["title"]} ({duration:.1f}s)', flush=True)

run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-loop', '1', '-framerate', '30',
     '-i', str(ROOT / 'outro.png'), '-t', '3', '-vf', 'format=yuv420p', '-an', '-c:v', 'libx264',
     '-preset', 'veryfast', '-crf', '16', '-threads', '4', str(ROOT / 'outro.mp4')])
concat_text = '\n'.join(f"file 'chapter_{i:02}.mp4'" for i in range(len(PLAN))) + "\nfile 'outro.mp4'\n"
(ROOT / 'concat.txt').write_text(concat_text)
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt',
     '-i', 'narration_raw.wav', '-vf',
     f'ass=captions.ass,fade=t=in:st=0:d=0.2,fade=t=out:st={timeline+2.4:.3f}:d=0.6',
     '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000',
     '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
     '-threads', '4', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
     '-movflags', '+faststart', '-t', f'{timeline+3:.6f}', '-metadata', 'title=Loan Default Risk - Guided Demo',
     '-metadata', 'comment=Edited screen recording with locally generated synthetic English narration.',
     'Loan_Risk_Demo_Edited.mp4'])
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'Loan_Risk_Demo_Edited.mp4',
     '-vn', '-c:a', 'libmp3lame', '-q:a', '2', 'Voiceover.mp3'])
print(f'DONE: {timeline+3:.2f} seconds', flush=True)
