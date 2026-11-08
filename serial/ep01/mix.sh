#!/bin/bash
# usage: ./mix.sh [voice_file]  -> out/audio_final.wav ; затем mux.sh
set -e; cd "$(dirname "$0")"
V="$1"
ffmpeg -y -loglevel error -i audio/bed.wav -i audio/fx.wav -filter_complex \
"[0]loudnorm=I=-36.5:TP=-3:LRA=7[b];[1]loudnorm=I=-33.5:TP=-3:LRA=11[f];[b][f]amix=inputs=2:normalize=0:duration=longest,apad=whole_dur=75[bg]" -map "[bg]" -ar 48000 -ac 2 out/bg.wav
if [ -n "$V" ]; then
 # голос: нормализация -14 LUFS, фон тише голоса на ~19 дБ
 ffmpeg -y -loglevel error -i "$V" -i out/bg.wav -filter_complex \
 "[0]loudnorm=I=-14:TP=-1.5:LRA=7,apad=whole_dur=75,aresample=48000,pan=stereo|c0=c0|c1=c0[v];[v][1]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9[o]" -map "[o]" -t 75 out/audio_final.wav
else
 ffmpeg -y -loglevel error -i out/bg.wav -af "loudnorm=I=-24:TP=-3:LRA=9" -t 75 out/audio_final.wav
fi
