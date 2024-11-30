#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cstdio>
#include <thread>
#include <atomic>
#include <regex>
#include <cstring>
#include <portaudio.h>
#include <sndfile.h>
#include <queue>
#include <mutex>
#include <csignal>
#include <condition_variable>
#include "common-sdl.h"
#include "common.h"
#include "whisper.h"
#include <cassert>
#include <vector>
#include "json.hpp"


/* 


                        █▄▄ █▀▀ █▀▄▀█ █▀█
                        █▄█ ██▄ █░▀░█ █▄█



⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣴⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠰⣿⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡄⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡆⠀⠀⣀⣴⠾⠛⠛⢻⣆⠀⠀⠀⠀⠀⠀⠀⠀⣸⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⡶⠟⠋⠉⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⢠⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡇⠀⠀⠀⠀⠀⠀⣾⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⠀⠀⠀⢸⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⢠⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠛⠻⠀⠂⠐⠀⠂⢰⠀⡦⢰⡶⣶⢈⢈⣧⣴⡀⣶⣾⢠⣆⣨⡠⠇⠸⠀⠁⢨⠀⠁⢨⠁⠁⠘⣶⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣠⣶⣶⣷⣶⣶⣷⣶⣶⣶⣾⣶⣷⣾⣶⣷⣾⣶⣶⣾⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣦⡄⠀⠛⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠈⢻⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢿⡆⠁⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⢻⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⣸⠄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⠀⢻⣿⣿⡿⢿⣟⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠿⣿⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠅⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⢸⣿⣿⡇⣼⣿⣧⡌⠉⠉⠉⠉⢹⣿⡭⣽⣿⣿⣿⡭⣶⣯⡀⠈⠉⠉⠩⣯⣽⣭⡍⣿⣿⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠈⣿⣿⣿⡜⣿⣿⣦⡀⠀⠠⢀⣼⡿⣽⣿⣿⣿⣿⣧⢻⣿⣄⠀⠀⠀⣰⣿⣿⡟⣸⣿⣿⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠐⣿⣿⣿⣿⣌⡻⠿⣿⣶⣶⠿⣻⣷⣿⣿⣿⣿⣿⣿⣷⣙⠿⣷⣶⣾⣿⠿⢫⣼⣿⣿⣿⠀⢀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠀⣿⣿⣿⣿⣿⣿⣷⣾⣾⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⡏⠻⣿⣶⣿⣷⣶⣿⣿⣿⣿⣿⣿⠀⢨⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣛⠿⣿⣿⣿⡿⢟⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⢺⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣾⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⢨⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⠀⠀⠀⢸⡇⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣆⠀⠀⠈⣿⣧⠀⠙⣟⠛⢛⡛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⢛⠛⡛⢛⢛⡛⢛⢛⡛⡉⢀⣀⣼⠀⠀⣰⣷⡀⠀⠀⠀⠀
⢠⣴⣶⣶⣿⣿⣿⣷⣤⣄⣈⣻⣻⣿⣿⣿⣿⣿⡿⢿⠻⠟⠿⡛⠿⠻⢟⠿⠻⡟⠿⠻⠟⠿⡛⠿⣿⣛⣿⣿⣿⣿⣿⣿⣿⣯⣤⣴⣿⣿⣿⣷⣶⣶⡄
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⡆⢑⢊⠱⠜⡰⢉⠂⠌⡑⡘⢆⠫⠜⡰⢁⡒⢡⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⠈⢿⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⣿⡆⠌⡘⢂⠡⡉⠞⡓⢶⣡⠈⡑⢃⠰⠁⣾⡛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠿⠿⣿⣿⣿⣿⡿⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠐⠀⠂⢦⠙⠘⠄⠂⠙⢷⡄⠀⠂⠡⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣵⣤⣵⠾⣀⠣⠡⠐⡈⠡⡘⢻⣷⣤⣶⣾⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠢⢅⠂⠡⠐⢀⠡⣘⢱⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡡⢂⠉⠀⠄⠂⡐⠤⣻⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣷⢥⣊⣴⣈⣖⡱⢮⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡿⠿⢾⣿⣷⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡇⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡇⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣯⠀⣾⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⠀⢹⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⠀⢸⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⢿⡿⣿⡄⣸⡿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡉⣿⣿⡇⣿⡏⢳⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⡇⢻⣿⣿⣿⣿⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠉⠀⠀⠉⠻⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀


*/

using namespace std;
using json = nlohmann::json;
#define BEMO ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL)


atomic<bool> running(true);
bool recording = false;
whisper_context *ctx = nullptr;
string recordedAudioFile = "recorded_audio.wav";
std::queue<nlohmann::json> jsonQueue;
std::mutex queueMutex;
std::condition_variable queueCondition;
std::atomic<bool> isWriting(true); 
// int c = 0;

json transcription_output = json::array();
struct whisper_params {
    int32_t n_threads  = std::min(4, (int32_t) std::thread::hardware_concurrency());
    int32_t step_ms    = 3000;
    int32_t length_ms  = 10000;
    int32_t keep_ms    = 200;
    int32_t capture_id = -1;
    int32_t max_tokens = 32;
    int32_t audio_ctx  = 0;

    float vad_thold    = 0.6f;
    float freq_thold   = 100.0f;

    bool translate     = false;
    bool no_fallback   = false;
    bool print_special = false;
    bool no_context    = true;
    bool no_timestamps = false;
    bool tinydiarize   = false;
    bool save_audio    = false; // save audio to wav file
    bool use_gpu       = true;
    bool flash_attn    = false;

    std::string language  = "en";
    std::string model     = "models/ggml-base.en.bin";
    std::string fname_out;
};

void whisper_print_usage(int argc, char ** argv, const whisper_params & params);

static bool whisper_params_parse(int argc, char ** argv, whisper_params & params) {
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            whisper_print_usage(argc, argv, params);
            exit(0);
        }
        else if (arg == "-t"    || arg == "--threads")       { params.n_threads     = std::stoi(argv[++i]); }
        else if (                  arg == "--step")          { params.step_ms       = std::stoi(argv[++i]); }
        else if (                  arg == "--length")        { params.length_ms     = std::stoi(argv[++i]); }
        else if (                  arg == "--keep")          { params.keep_ms       = std::stoi(argv[++i]); }
        else if (arg == "-c"    || arg == "--capture")       { params.capture_id    = std::stoi(argv[++i]); }
        else if (arg == "-mt"   || arg == "--max-tokens")    { params.max_tokens    = std::stoi(argv[++i]); }
        else if (arg == "-ac"   || arg == "--audio-ctx")     { params.audio_ctx     = std::stoi(argv[++i]); }
        else if (arg == "-vth"  || arg == "--vad-thold")     { params.vad_thold     = std::stof(argv[++i]); }
        else if (arg == "-fth"  || arg == "--freq-thold")    { params.freq_thold    = std::stof(argv[++i]); }
        else if (arg == "-tr"   || arg == "--translate")     { params.translate     = true; }
        else if (arg == "-nf"   || arg == "--no-fallback")   { params.no_fallback   = true; }
        else if (arg == "-ps"   || arg == "--print-special") { params.print_special = true; }
        else if (arg == "-kc"   || arg == "--keep-context")  { params.no_context    = false; }
        else if (arg == "-l"    || arg == "--language")      { params.language      = argv[++i]; }
        else if (arg == "-m"    || arg == "--model")         { params.model         = argv[++i]; }
        else if (arg == "-f"    || arg == "--file")          { params.fname_out     = argv[++i]; }
        else if (arg == "-tdrz" || arg == "--tinydiarize")   { params.tinydiarize   = true; }
        else if (arg == "-sa"   || arg == "--save-audio")    { params.save_audio    = true; }
        else if (arg == "-ng"   || arg == "--no-gpu")        { params.use_gpu       = false; }
        else if (arg == "-fa"   || arg == "--flash-attn")    { params.flash_attn    = true; }

        else {
            fprintf(stderr, "error: unknown argument: %s\n", arg.c_str());
            whisper_print_usage(argc, argv, params);
            exit(0);
        }
    }

    return true;
}

void whisper_print_usage(int /*argc*/, char ** argv, const whisper_params & params) {
    fprintf(stderr, "\n");
    fprintf(stderr, "usage: %s [options]\n", argv[0]);
    fprintf(stderr, "\n");
    fprintf(stderr, "options:\n");
    fprintf(stderr, "  -h,       --help          [default] show this help message and exit\n");
    fprintf(stderr, "  -t N,     --threads N     [%-7d] number of threads to use during computation\n",    params.n_threads);
    fprintf(stderr, "            --step N        [%-7d] audio step size in milliseconds\n",                params.step_ms);
    fprintf(stderr, "            --length N      [%-7d] audio length in milliseconds\n",                   params.length_ms);
    fprintf(stderr, "            --keep N        [%-7d] audio to keep from previous step in ms\n",         params.keep_ms);
    fprintf(stderr, "  -c ID,    --capture ID    [%-7d] capture device ID\n",                              params.capture_id);
    fprintf(stderr, "  -mt N,    --max-tokens N  [%-7d] maximum number of tokens per audio chunk\n",       params.max_tokens);
    fprintf(stderr, "  -ac N,    --audio-ctx N   [%-7d] audio context size (0 - all)\n",                   params.audio_ctx);
    fprintf(stderr, "  -vth N,   --vad-thold N   [%-7.2f] voice activity detection threshold\n",           params.vad_thold);
    fprintf(stderr, "  -fth N,   --freq-thold N  [%-7.2f] high-pass frequency cutoff\n",                   params.freq_thold);
    fprintf(stderr, "  -tr,      --translate     [%-7s] translate from source language to english\n",      params.translate ? "true" : "false");
    fprintf(stderr, "  -nf,      --no-fallback   [%-7s] do not use temperature fallback while decoding\n", params.no_fallback ? "true" : "false");
    fprintf(stderr, "  -ps,      --print-special [%-7s] print special tokens\n",                           params.print_special ? "true" : "false");
    fprintf(stderr, "  -kc,      --keep-context  [%-7s] keep context between audio chunks\n",              params.no_context ? "false" : "true");
    fprintf(stderr, "  -l LANG,  --language LANG [%-7s] spoken language\n",                                params.language.c_str());
    fprintf(stderr, "  -m FNAME, --model FNAME   [%-7s] model path\n",                                     params.model.c_str());
    fprintf(stderr, "  -f FNAME, --file FNAME    [%-7s] text output file name\n",                          params.fname_out.c_str());
    fprintf(stderr, "  -tdrz,    --tinydiarize   [%-7s] enable tinydiarize (requires a tdrz model)\n",     params.tinydiarize ? "true" : "false");
    fprintf(stderr, "  -sa,      --save-audio    [%-7s] save the recorded audio to a file\n",              params.save_audio ? "true" : "false");
    fprintf(stderr, "  -ng,      --no-gpu        [%-7s] disable GPU inference\n",                          params.use_gpu ? "false" : "true");
    fprintf(stderr, "  -fa,      --flash-attn    [%-7s] flash attention during inference\n",               params.flash_attn ? "true" : "false");
    fprintf(stderr, "\n");
}

/*/--------------------------------------------------------------------------------*/
void trimSilence(std::vector<int16_t>& audioBuffer, int silenceThreshold = 200);
std::vector<float> resampleAudio(const std::vector<int16_t>& input, int inputRate, int outputRate);
std::string processAudioChunk(whisper_context* ctx, const float* audioData, size_t length);
void finalizeJsonFile();
void initializeJsonFile();
#include <fstream>

void saveAudioToFile(const std::vector<float>& audio, const std::string& filename) {
    std::ofstream outFile(filename, std::ios::binary);
    for (float sample : audio) {
        int16_t intSample = static_cast<int16_t>(sample * 32767); // Convert to 16-bit PCM
        outFile.write(reinterpret_cast<const char*>(&intSample), sizeof(int16_t));
    }
    outFile.close();
    std::cout << "Saved audio to " << filename << "\n";
}


void processRealTimeAudio(whisper_context* ctx, int inputSampleRate = 44100, int targetSampleRate = 16000) {
    const size_t requiredSamples = targetSampleRate;  // 1 second of audio at the target rate
    std::vector<int16_t> audioBuffer;
    int16_t buffer[1024];

    PaStream* stream;
    PaError err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "PortAudio initialization error: " << Pa_GetErrorText(err) << "\n";
        return;
    }

    PaStreamParameters inputParameters;
    inputParameters.device = Pa_GetDefaultInputDevice();
    inputParameters.channelCount = 1;  // Mono
    inputParameters.sampleFormat = paInt16;
    inputParameters.suggestedLatency = Pa_GetDeviceInfo(inputParameters.device)->defaultLowInputLatency;
    inputParameters.hostApiSpecificStreamInfo = NULL;

    // Open stream
    err = Pa_OpenStream(&stream, &inputParameters, NULL, inputSampleRate, 1024, paClipOff, NULL, NULL);
    if (err != paNoError) {
        std::cerr << "Stream open error: " << Pa_GetErrorText(err) << "\n";
        Pa_Terminate();
        return;
    }

    // Start stream
    err = Pa_StartStream(stream);
    if (err != paNoError) {
        std::cerr << "Stream start error: " << Pa_GetErrorText(err) << "\n";
        Pa_CloseStream(stream);
        Pa_Terminate();
        return;
    }

    std::cout << "Stream started. Listening for audio...\n";

    while (true) {
        err = Pa_ReadStream(stream, buffer, 1024);
        if (err && err != paInputOverflowed) {
            std::cerr << "Error reading audio from stream: " << Pa_GetErrorText(err) << "\n";
            break;
        }

        // Append captured audio to buffer
        audioBuffer.insert(audioBuffer.end(), buffer, buffer + 1024);

        // Process audio if enough samples are collected
        if (audioBuffer.size() >= requiredSamples) {
            trimSilence(audioBuffer);  // Remove silence
            std::vector<float> resampledAudio = resampleAudio(audioBuffer, inputSampleRate, targetSampleRate);

            // Transcribe using Whisper
            std::string transcription = processAudioChunk(ctx, resampledAudio.data(), resampledAudio.size());
            std::cout << "Transcription: " << transcription << "\n";

            audioBuffer.clear();  // Clear buffer after processing
        }
    }

    Pa_StopStream(stream);
    Pa_CloseStream(stream);
    Pa_Terminate();
}
void initializeWhisper(const std::string &modelPath) {
    whisper_context_params ctx_params = whisper_context_default_params();

    // Adjust any context-specific parameters here, if necessary
    ctx = whisper_init_from_file_with_params(modelPath.c_str(), ctx_params);

    if (!ctx) {
        cerr << "Failed to initialize Whisper context with the provided model.\n";
        return;
    }
}

std::string processAudioChunk(whisper_context* ctx, const float* audioData, size_t length) {
    whisper_full_params params = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);

    params.print_progress = true;  // Enable progress printing
    params.language = "en";        // Set the language to English

    if (whisper_full(ctx, params, audioData, length) != 0) {
        std::cerr << "Failed to process audio with Whisper.\n";
        return "";
    }

    std::string transcription;
    for (int i = 0; i < whisper_full_n_segments(ctx); ++i) {
        transcription += whisper_full_get_segment_text(ctx, i);
    }

    return transcription;
}


void trimSilence(std::vector<int16_t>& audioBuffer, int silenceThreshold) {
    audioBuffer.erase(std::remove_if(audioBuffer.begin(), audioBuffer.end(),
                                     [silenceThreshold](int16_t sample) {
                                         return std::abs(sample) < silenceThreshold;
                                     }),
                      audioBuffer.end());
}


/*---------------------record -------------------------------------------- */

void recordAudio(const std::string &outputFile, int numSeconds = 5) {
    PaError err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "PortAudio init error: " << Pa_GetErrorText(err) << std::endl;
        return;
    }

    // Setup parameters
    PaStreamParameters inputParameters;
    const int sampleRate = 16000; // Target sample rate
    const int framesPerBuffer = 1024;
    const int numChannels = 1;   // Mono

    // Find default device
    inputParameters.device = Pa_GetDefaultInputDevice();
    if (inputParameters.device == paNoDevice) {
        std::cerr << "No default input device." << std::endl;
        Pa_Terminate();
        return;
    }
    inputParameters.channelCount = numChannels;
    inputParameters.sampleFormat = paInt16;
    inputParameters.suggestedLatency = Pa_GetDeviceInfo(inputParameters.device)->defaultLowInputLatency;
    inputParameters.hostApiSpecificStreamInfo = nullptr;

    // Open stream
    PaStream *stream;
    err = Pa_OpenStream(&stream, &inputParameters, nullptr, sampleRate, framesPerBuffer, paClipOff, nullptr, nullptr);
    if (err != paNoError) {
        std::cerr << "Stream open error: " << Pa_GetErrorText(err) << std::endl;
        Pa_Terminate();
        return;
    }

    // Start stream
    err = Pa_StartStream(stream);
    if (err != paNoError) {
        std::cerr << "Stream start error: " << Pa_GetErrorText(err) << std::endl;
        Pa_CloseStream(stream);
        Pa_Terminate();
        return;
    }

    // Prepare WAV file
    SF_INFO sfinfo;
    sfinfo.channels = numChannels;
    sfinfo.samplerate = sampleRate;
    sfinfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;
    SNDFILE *outfile = sf_open(outputFile.c_str(), SFM_WRITE, &sfinfo);
    if (!outfile) {
        std::cerr << "Error opening WAV file: " << sf_strerror(nullptr) << std::endl;
        Pa_StopStream(stream);
        Pa_CloseStream(stream);
        Pa_Terminate();
        return;
    }

    // Record for numSeconds
    std::vector<int16_t> buffer(framesPerBuffer);
    for (int i = 0; i < sampleRate * numSeconds / framesPerBuffer; ++i) {
        err = Pa_ReadStream(stream, buffer.data(), framesPerBuffer);
        if (err && err != paInputOverflowed) {
            std::cerr << "Stream read error: " << Pa_GetErrorText(err) << std::endl;
            break;
        }
        sf_write_short(outfile, buffer.data(), framesPerBuffer);
    }

    // Cleanup
    sf_close(outfile);
    Pa_StopStream(stream);
    Pa_CloseStream(stream);
    Pa_Terminate();

    std::cout << "Recording complete. File saved to: " << outputFile << std::endl;
}



/*------------------------------------clean text-------------------------- */

string cleanText(const string &input)
{
    string output = regex_replace(input, regex("\033\\[[0-9;]*[mK]"), "");
    output.erase(0, output.find_first_not_of(" \t\n\r")); // Trim left
    output.erase(output.find_last_not_of(" \t\n\r") + 1); // Trim right
    return output;
}

/*---------------------------------------classify--------------------------*/
string classifyEvent(const string &line,int c)
{

    //  cout<<"lllllllllllllllll : "<<c<<" " <<line<<endl;
    if (line.find("bemo") != string::npos ||
        line.find("bmo") != string::npos ||
        line.find("vemo") != string::npos ||
        line.find("vmo") != string::npos ||
        line.find("nemo") != string::npos ||
        line.find("kemo") != string::npos ||
        line.find("bbmo") != string::npos ||
        line.find("moo") != string::npos ||
        line.find("bemoo") != string::npos||
        line.find("bemu") != string::npos||
        line.find("temo") != string::npos){
        return "bemo";
    }
    /*---------------------------------------------------------- */
    else if (line.find("screaming") != string::npos)
        return "screaming";
    /*---------------------------------------------------------- */

    else if (line.find("music") != string::npos)
    {
        if (line.find("dramatic") != string::npos)
        {
            return "dramatic_music";
        }
        return "music";
    }
   /*---------------------------------------------------------- */

    else if (line.find("blank audio") != string::npos)
        return "blank_audio";
    /*---------------------------------------------------------- */

    else if (line.find("crowd talking") != string::npos)
        return "crowd_talking";
    
    /*---------------------------------------------------------- */

    else if (line.find("laughing") != string::npos)
        return "laughing";
    
    /*---------------------------------------------------------- */

   return "other";
}
/*---------------------------------------initialize json--------------- */
void initializeJsonFile() {
    std::ofstream outFile("transcriptions.json");
    outFile << "[";  // Start the JSON array
    outFile.close();
}
/*---------------------------------------clear json if exceeds size--------------- */
void clearJsonFileIfExceedsSize()
{
    const long long MAX_SIZE = 50 * 1024 * 1024; 
    ifstream inFile("transcriptions.json", ios::ate | ios::binary);
    if (inFile.tellg() >= MAX_SIZE)
    {
        inFile.close();
        ofstream outFile("transcriptions.json", ios::trunc);
        outFile.close();
        cout << "Cleared transcriptions.json as it exceeded 50 MB" << "\n";
        initializeJsonFile();

    }
    else
    {
        inFile.close();
    }
}

/*---------------------------------------close json--------------------- */
void finalizeJsonFile() {
    std::ifstream inFile("transcriptions.json");
    std::string content((std::istreambuf_iterator<char>(inFile)), std::istreambuf_iterator<char>());
    inFile.close();

    // Remove trailing comma and close the JSON array
    if (!content.empty() && content.back() == ',') {
        content.pop_back();
    }

    std::ofstream outFile("transcriptions.json", std::ios::trunc);
    outFile << content << "]";
    outFile.close();
}


/*---------------------------------------remove closing bracket--------------- */
void removeClosingBracket()
{
    ifstream inFile("transcriptions.json");
    if (!inFile.is_open())
    {
        cerr << "Failed to open transcriptions.json" << "\n";
        return;
    }

    string content((istreambuf_iterator<char>(inFile)), istreambuf_iterator<char>());
    inFile.close();

    if (!content.empty() && content.back() == ']')
    {
        content.pop_back(); // Remove the last character
        ofstream outFile("transcriptions.json", ios::trunc);
        outFile << content;
        outFile.close();
        // cout << "Removed closing bracket from transcriptions.json" << "\n";
    }
}


void jsonWriterThread(const std::string &filename) {
    std::ofstream outFile(filename, std::ios::trunc);
    if (!outFile.is_open()) {
        std::cerr << "Failed to open JSON file for writing: " << filename << "\n";
        return;
    }

    outFile << "["; // Start the JSON array
    bool isFirst = true;

    while (isWriting || !jsonQueue.empty()) {
        nlohmann::json event;

        {
            std::unique_lock<std::mutex> lock(queueMutex);
            if (jsonQueue.empty() && !isWriting) {
                break; // Exit if writing is done and the queue is empty
            }
            queueCondition.wait(lock, [] { return !jsonQueue.empty() || !isWriting; });

            if (!jsonQueue.empty()) {
                event = jsonQueue.front();
                jsonQueue.pop();
            }
        }

        if (!event.is_null()) {
            std::lock_guard<std::mutex> fileLock(fileMutex);
            if (!isFirst) {
                outFile << ",";
            }
            outFile << event.dump(4); // Write JSON with indentation
            isFirst = false;
        }
    }

    outFile << "]"; // Close the JSON array
    outFile.close();
}

// Function to process transcription and enqueue it for JSON writing
void processTranscription(whisper_context *ctx, const whisper_params &params, double pcmf32_size, std::chrono::high_resolution_clock::time_point t_last, std::chrono::high_resolution_clock::time_point t_start) {
    const int n_segments = whisper_full_n_segments(ctx);

    for (int i = 0; i < n_segments; ++i) {
        const char *text = whisper_full_get_segment_text(ctx, i);

        double start_time = 0.0;
        double end_time = 0.0;

        if (!params.no_timestamps) {
            const int64_t t0 = whisper_full_get_segment_t0(ctx, i);
            const int64_t t1 = whisper_full_get_segment_t1(ctx, i);
            start_time = t0 / 100.0;
            end_time = t1 / 100.0;
        }

        nlohmann::json event;
        event["raw_text"] = text;
        event["cleaned_text"] = text; // Adjust cleaning logic if needed
        event["classification"] = "speech";
        event["start_time"] = start_time;
        event["end_time"] = end_time;

        // Add event to the queue
        {
            std::lock_guard<std::mutex> lock(queueMutex);
            jsonQueue.push(event);
        }
        queueCondition.notify_one();
    }
}


/*----------------------------read .wavvv--------------------*/


/*--------------------------------------stream---------------------*/
std::vector<float> resampleAudio(const std::vector<int16_t>& input, int inputRate, int outputRate) {
    size_t inputSize = input.size();
    size_t outputSize = inputSize * outputRate / inputRate;

    std::vector<float> output(outputSize);
    for (size_t i = 0; i < outputSize; ++i) {
        float inputIndex = i * (float)inputRate / outputRate;
        size_t index = (size_t)inputIndex;

        if (index + 1 < inputSize) {
            float frac = inputIndex - index;
            output[i] = (1 - frac) * input[index] + frac * input[index + 1];
        } else {
            output[i] = input[index];
        }
    }

    return output;
}

void selectAudioDevice(PaStreamParameters &inputParameters) {
    int defaultDeviceIndex = Pa_GetDefaultInputDevice();
    if (defaultDeviceIndex == paNoDevice) {
        cerr << "No default input device found.\n";
        exit(1);
    }

    const PaDeviceInfo *deviceInfo = Pa_GetDeviceInfo(defaultDeviceIndex);
    cout << "Using Default Input Device: " << deviceInfo->name << "\n";

    inputParameters.device = defaultDeviceIndex;
    inputParameters.channelCount = 1; // Mono input
    inputParameters.sampleFormat = paInt16;
    inputParameters.suggestedLatency = deviceInfo->defaultLowInputLatency;
    inputParameters.hostApiSpecificStreamInfo = NULL;
}

void executeStreamCommand() {
    PaError err;

    // Initialize PortAudio
    err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "Failed to initialize PortAudio: " << Pa_GetErrorText(err) << "\n";
        return;
    }

    // Configure the input parameters
    PaStreamParameters inputParameters;
    selectAudioDevice(inputParameters);

    double inputSampleRate = Pa_GetDeviceInfo(inputParameters.device)->defaultSampleRate;
    double targetSampleRate = 16000;

    // Open the audio stream
    PaStream *stream;
    err = Pa_OpenStream(&stream, &inputParameters, NULL, inputSampleRate, 1024, paClipOff, NULL, NULL);
    if (err != paNoError) {
        std::cerr << "Failed to open PortAudio stream: " << Pa_GetErrorText(err) << "\n";
        Pa_Terminate();
        return;
    }

    // Start the stream
    err = Pa_StartStream(stream);
    if (err != paNoError) {
        std::cerr << "Failed to start PortAudio stream: " << Pa_GetErrorText(err) << "\n";
        Pa_CloseStream(stream);
        Pa_Terminate();
        return;
    }

    std::cout << "Stream started. Listening for audio...\n";

    // Set up WAV file
    SF_INFO sfinfo = {0};
    sfinfo.channels = 1;                 // Mono
    sfinfo.samplerate = targetSampleRate; // Target sample rate
    sfinfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;

    SNDFILE *outfile = sf_open("recorded_audio.wav", SFM_WRITE, &sfinfo);
    if (!outfile) {
        std::cerr << "Failed to open WAV file for writing: " << sf_strerror(nullptr) << "\n";
        Pa_CloseStream(stream);
        Pa_Terminate();
        return;
    }

    // ** New additions start here **
    std::vector<int16_t> audioBuffer; // Buffer to accumulate audio samples
    const size_t requiredSamples = 32000; // 1 second of audio at 16 kHz
    int16_t buffer[1024];

    // Loop to read audio data
while (running) {
    err = Pa_ReadStream(stream, buffer, 1024);
    if (err && err != paInputOverflowed) {
        std::cerr << "Error reading audio from stream: " << Pa_GetErrorText(err) << "\n";
        break;
    } else if (err == paInputOverflowed) {
        std::cerr << "Input overflow occurred. Data may be lost.\n";
    }

    // Log the number of samples captured
   // std::cout << "Captured " << 1024 << " samples of audio.\n";

    // Append the new samples to the buffer
    audioBuffer.insert(audioBuffer.end(), buffer, buffer + 1024);

    // Ensure at least 1 second of data before processing
if (audioBuffer.size() >= requiredSamples) {
    std::vector<float> resampledAudio = resampleAudio(audioBuffer, inputSampleRate, targetSampleRate);

    // Save resampled audio for debugging
    saveAudioToFile(resampledAudio, "debug_audio.raw");

    if (resampledAudio.size() < requiredSamples) {
        size_t paddingSize = requiredSamples - resampledAudio.size();
        resampledAudio.insert(resampledAudio.end(), paddingSize, 0.0f);
        std::cout << "Added " << paddingSize << " samples of silence for padding.\n";
    }

std::string transcription = processAudioChunk(ctx, resampledAudio.data(), resampledAudio.size());
    std::cout << "Transcription: " << transcription << "\n";
    audioBuffer.clear(); // Clear buffer after processing
}

    // Write raw audio to WAV file
    sf_write_short(outfile, buffer, 1024);
}

    // ** New additions end here **

    // Stop and close the stream
    err = Pa_StopStream(stream);
    if (err != paNoError) {
        std::cerr << "Failed to stop PortAudio stream: " << Pa_GetErrorText(err) << "\n";
    }

    err = Pa_CloseStream(stream);
    if (err != paNoError) {
        std::cerr << "Failed to close PortAudio stream: " << Pa_GetErrorText(err) << "\n";
    }

    // Close WAV file
    sf_close(outfile);

    // Terminate PortAudio
    Pa_Terminate();

    std::cout << "Stream stopped.\n";
}


void listAudioDevices() {
    PaError err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "Failed to initialize PortAudio: " << Pa_GetErrorText(err) << std::endl;
        return;
    }

    int numDevices = Pa_GetDeviceCount();
    if (numDevices < 0) {
        std::cerr << "Error getting device count: " << Pa_GetErrorText(numDevices) << std::endl;
        Pa_Terminate();
        return;
    }

    std::cout << "Available Audio Devices:" << std::endl;
    for (int i = 0; i < numDevices; ++i) {
        const PaDeviceInfo *deviceInfo = Pa_GetDeviceInfo(i);
        std::cout << "ID: " << i << ", Name: " << deviceInfo->name
                  << ", Default Sample Rate: " << deviceInfo->defaultSampleRate << " Hz" << std::endl;
    }

    Pa_Terminate();
}


// int main() {
//     const std::string jsonFilename = "transcriptions.json";

//     // List available audio devices
//     listAudioDevices();
//     return 0;
// }



/*
//////////////////////////////////////////////

for install jsoncpp:
sudo apt-get install libjsoncpp-dev
------------------------------------------

for install libsndfile:
sudo apt-get install libsndfile1-dev
------------------------------------------

for install portaudio:
sudo apt-get install libportaudio2

//////////////////////////////////////////////

there are two ways to run the program:
1. to run the program in stream mode, uncomment the first main function or comment the second main function
2. to run the program in file mode,

-------------------------------------------
for first main function, you can run the program by typing the following command:
g++ -std=c++11 -o w w.cpp -ljsoncpp -lpthread
./w
-------------------------------------------
for the second main function, you can run the program by typing the following command:
g++ -std=c++11 -o w w.cpp -ljsoncpp -lpthread
./w <path_to_wav_file>
-------------------------------------------

 */

void signalHandler(int signum) {
    std::cout << "\nInterrupt signal (" << signum << ") received. Terminating...\n";
    running = false;
}
// int main() {
//     // Initialize Whisper model
// whisper_context_params ctx_params = whisper_context_default_params();
// whisper_context* ctx = whisper_init_from_file_with_params("models/ggml-base.en.bin", ctx_params);
//     if (!ctx) {
//         std::cerr << "Failed to initialize Whisper model.\n";
//         return 1;
//     }

//     initializeJsonFile();  // Start JSON logging

//     processRealTimeAudio(ctx);  // Process real-time audio

//     finalizeJsonFile();  // Finalize JSON logging

//     whisper_free(ctx);  // Free Whisper resources
//     return 0;
// }





/////////////////////////////////////////////////////////////////////////////////////////////////////////////
 
// int main(int argc, char *argv[])
// {
//   //  BEMO;
//     if (argc < 2)
//     {
//         cerr << "Usage: " << argv[0] << " <path_to_wav_file>" << "\n";
//         return 1;
//     }
//     string wavFile = argv[1];
//         std::cout << "Calling finalizeJsonFile()" << std::endl;

//     clearJsonFileIfExceedsSize();
//     initializeJsonFile();
//     executeMainCommand(wavFile);
//     // cout<<"heheheheheheheheheheheee\n";
//     finalizeJsonFile();
//     return 0;
// }

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

// Real-time speech recognition of input from a microphone
//
// A very quick-n-dirty implementation serving mainly as a proof of concept.
//


int main(int argc, char ** argv) {
    whisper_params params;

    if (whisper_params_parse(argc, argv, params) == false) {
        return 1;
    }

    params.keep_ms   = std::min(params.keep_ms,   params.step_ms);
    params.length_ms = std::max(params.length_ms, params.step_ms);

    const int n_samples_step = (1e-3*params.step_ms  )*WHISPER_SAMPLE_RATE;
    const int n_samples_len  = (1e-3*params.length_ms)*WHISPER_SAMPLE_RATE;
    const int n_samples_keep = (1e-3*params.keep_ms  )*WHISPER_SAMPLE_RATE;
    const int n_samples_30s  = (1e-3*30000.0         )*WHISPER_SAMPLE_RATE;

    const bool use_vad = n_samples_step <= 0; // sliding window mode uses VAD

    const int n_new_line = !use_vad ? std::max(1, params.length_ms / params.step_ms - 1) : 1; // number of steps to print new line

    params.no_timestamps  = !use_vad;
    params.no_context    |= use_vad;
    params.max_tokens     = 0;

    // init audio

    audio_async audio(params.length_ms);
    if (!audio.init(params.capture_id, WHISPER_SAMPLE_RATE)) {
        fprintf(stderr, "%s: audio.init() failed!\n", __func__);
        return 1;
    }

    audio.resume();

    // whisper init
    if (params.language != "auto" && whisper_lang_id(params.language.c_str()) == -1){
        fprintf(stderr, "error: unknown language '%s'\n", params.language.c_str());
        whisper_print_usage(argc, argv, params);
        exit(0);
    }

    struct whisper_context_params cparams = whisper_context_default_params();

    cparams.use_gpu    = params.use_gpu;
    cparams.flash_attn = params.flash_attn;

    struct whisper_context * ctx = whisper_init_from_file_with_params(params.model.c_str(), cparams);

    std::vector<float> pcmf32    (n_samples_30s, 0.0f);
    std::vector<float> pcmf32_old;
    std::vector<float> pcmf32_new(n_samples_30s, 0.0f);

    std::vector<whisper_token> prompt_tokens;

    // print some info about the processing
    {
        fprintf(stderr, "\n");
        if (!whisper_is_multilingual(ctx)) {
            if (params.language != "en" || params.translate) {
                params.language = "en";
                params.translate = false;
                fprintf(stderr, "%s: WARNING: model is not multilingual, ignoring language and translation options\n", __func__);
            }
        }
        fprintf(stderr, "%s: processing %d samples (step = %.1f sec / len = %.1f sec / keep = %.1f sec), %d threads, lang = %s, task = %s, timestamps = %d ...\n",
                __func__,
                n_samples_step,
                float(n_samples_step)/WHISPER_SAMPLE_RATE,
                float(n_samples_len )/WHISPER_SAMPLE_RATE,
                float(n_samples_keep)/WHISPER_SAMPLE_RATE,
                params.n_threads,
                params.language.c_str(),
                params.translate ? "translate" : "transcribe",
                params.no_timestamps ? 0 : 1);

        if (!use_vad) {
            fprintf(stderr, "%s: n_new_line = %d, no_context = %d\n", __func__, n_new_line, params.no_context);
        } else {
            fprintf(stderr, "%s: using VAD, will transcribe on speech activity\n", __func__);
        }

        fprintf(stderr, "\n");
    }

    int n_iter = 0;

    bool is_running = true;

    std::ofstream fout;
    if (params.fname_out.length() > 0) {
        fout.open(params.fname_out);
        if (!fout.is_open()) {
            fprintf(stderr, "%s: failed to open output file '%s'!\n", __func__, params.fname_out.c_str());
            return 1;
        }
    }

    wav_writer wavWriter;
    // save wav file
    if (params.save_audio) {
        // Get current date/time for filename
        time_t now = time(0);
        char buffer[80];
        strftime(buffer, sizeof(buffer), "%Y%m%d%H%M%S", localtime(&now));
        std::string filename = std::string(buffer) + ".wav";

        wavWriter.open(filename, WHISPER_SAMPLE_RATE, 16, 1);
    }
    printf("[Start speaking]\n");
    fflush(stdout);

    auto t_last  = std::chrono::high_resolution_clock::now();
    const auto t_start = t_last;

    // main audio loop
    while (is_running) {
        if (params.save_audio) {
            wavWriter.write(pcmf32_new.data(), pcmf32_new.size());
        }
        // handle Ctrl + C
        is_running = sdl_poll_events();

        if (!is_running) {
            break;
        }

        // process new audio

        if (!use_vad) {
            while (true) {
                audio.get(params.step_ms, pcmf32_new);

                if ((int) pcmf32_new.size() > 2*n_samples_step) {
                    fprintf(stderr, "\n\n%s: WARNING: cannot process audio fast enough, dropping audio ...\n\n", __func__);
                    audio.clear();
                    continue;
                }

                if ((int) pcmf32_new.size() >= n_samples_step) {
                    audio.clear();
                    break;
                }

                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }

            const int n_samples_new = pcmf32_new.size();

            // take up to params.length_ms audio from previous iteration
            const int n_samples_take = std::min((int) pcmf32_old.size(), std::max(0, n_samples_keep + n_samples_len - n_samples_new));

            //printf("processing: take = %d, new = %d, old = %d\n", n_samples_take, n_samples_new, (int) pcmf32_old.size());

            pcmf32.resize(n_samples_new + n_samples_take);

            for (int i = 0; i < n_samples_take; i++) {
                pcmf32[i] = pcmf32_old[pcmf32_old.size() - n_samples_take + i];
            }

            memcpy(pcmf32.data() + n_samples_take, pcmf32_new.data(), n_samples_new*sizeof(float));

            pcmf32_old = pcmf32;
        } else {
            const auto t_now  = std::chrono::high_resolution_clock::now();
            const auto t_diff = std::chrono::duration_cast<std::chrono::milliseconds>(t_now - t_last).count();

            if (t_diff < 2000) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));

                continue;
            }

            audio.get(2000, pcmf32_new);

            if (::vad_simple(pcmf32_new, WHISPER_SAMPLE_RATE, 1000, params.vad_thold, params.freq_thold, false)) {
                audio.get(params.length_ms, pcmf32);
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));

                continue;
            }

            t_last = t_now;
        }

        // run the inference
        {
            whisper_full_params wparams = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);

            wparams.print_progress   = false;
            wparams.print_special    = params.print_special;
            wparams.print_realtime   = false;
            wparams.print_timestamps = !params.no_timestamps;
            wparams.translate        = params.translate;
            wparams.single_segment   = !use_vad;
            wparams.max_tokens       = params.max_tokens;
            wparams.language         = params.language.c_str();
            wparams.n_threads        = params.n_threads;

            wparams.audio_ctx        = params.audio_ctx;

            wparams.tdrz_enable      = params.tinydiarize; // [TDRZ]

            // disable temperature fallback
            //wparams.temperature_inc  = -1.0f;
            wparams.temperature_inc  = params.no_fallback ? 0.0f : wparams.temperature_inc;

            wparams.prompt_tokens    = params.no_context ? nullptr : prompt_tokens.data();
            wparams.prompt_n_tokens  = params.no_context ? 0       : prompt_tokens.size();

            if (whisper_full(ctx, wparams, pcmf32.data(), pcmf32.size()) != 0) {
                fprintf(stderr, "%s: failed to process audio\n", argv[0]);
                return 6;
            }

            // print result;
            {
//                const int n_segments = whisper_full_n_segments(ctx);
// nlohmann::json transcription_output = nlohmann::json::array(); // Initialize JSON array

// for (int i = 0; i < n_segments; ++i) {
//     const char* text = whisper_full_get_segment_text(ctx, i);

//     if (params.no_timestamps) {
//         printf("%s", text);
//         fflush(stdout);

//         // Add segment to JSON without timestamps
//         transcription_output.push_back({
//             {"raw_text", text},
//             {"cleaned_text", text}, // Assume raw text is already cleaned; update if needed
//             {"classification", "speech"}, // Default classification; adjust as needed
//             {"start_time", 0.0},
//             {"end_time", 0.0}
//         });
//     } else {
//         const int64_t t0 = whisper_full_get_segment_t0(ctx, i);
//         const int64_t t1 = whisper_full_get_segment_t1(ctx, i);

//         // Convert timestamps to seconds
//         double start_time = t0 / 100.0;
//         double end_time = t1 / 100.0;

//         // Add segment to JSON with timestamps
//         transcription_output.push_back({
//             {"raw_text", text},
//             {"cleaned_text", text}, // Assume raw text is already cleaned; update if needed
//             {"classification", "speech"}, // Default classification; adjust as needed
//             {"start_time", start_time},
//             {"end_time", end_time}
//         });

//         // Display output
//         std::string output = "[" + to_timestamp(t0, false) + " --> " + to_timestamp(t1, false) + "]  " + text;
//         printf("%s", output.c_str());
//         fflush(stdout);
//     }
// }

// // Save the JSON file
// std::ofstream json_file("transcription.json");
// if (json_file.is_open()) {
//     json_file << transcription_output.dump(4); // Pretty print JSON
//     json_file.close();
//     printf("\nTranscription saved to 'transcription.json'\n");
// } else {
//     fprintf(stderr, "Error: Unable to open JSON file for writing.\n");
// }
std::thread writerThread(jsonWriterThread, "transcriptions.json");

// Main transcription loop
while (is_running) {
    // Process audio (existing code)
    if (whisper_full(ctx, wparams, pcmf32.data(), pcmf32.size()) != 0) {
        fprintf(stderr, "Error: failed to process audio\n");
        break;
    }

    processTranscription(ctx, params, pcmf32.size(), t_last, t_start);
}

// Signal writer thread to finish
isWriting = false;
queueCondition.notify_all();
writerThread.join();

            }



            ++n_iter;

            if (!use_vad && (n_iter % n_new_line) == 0) {
                printf("\n");

                // keep part of the audio for next iteration to try to mitigate word boundary issues
                pcmf32_old = std::vector<float>(pcmf32.end() - n_samples_keep, pcmf32.end());

                // Add tokens of the last full length segment as the prompt
                if (!params.no_context) {
                    prompt_tokens.clear();

                    const int n_segments = whisper_full_n_segments(ctx);
                    for (int i = 0; i < n_segments; ++i) {
                        const int token_count = whisper_full_n_tokens(ctx, i);
                        for (int j = 0; j < token_count; ++j) {
                            prompt_tokens.push_back(whisper_full_get_token_id(ctx, i, j));
                        }
                    }
                }
            }
            fflush(stdout);
        }
    }

    audio.pause();

    whisper_print_timings(ctx);
    whisper_free(ctx);

    return 0;
}
