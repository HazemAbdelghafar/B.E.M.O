# Whisper_cpp

## Installation

```bash
sudo apt-get update
sudo apt-get install libportaudio2 libsndfile1-dev
sudo apt-get install ffmpeg
g++ -std=c++17 -o main main.cpp -lpthread -lportaudio -lsndfile
sudo apt-get install nlohmann-json3-dev
```

## Real Time

```bash
make stram
./stream -m ./models/ggml-base.en.bin -t 4 -c 0
```

## File

```bash
./stream <path_to_wav_file>
```
