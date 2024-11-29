#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cstdio>
#include <thread>
#include <atomic>
#include <regex>
#include <cstring>
#include<nlohmann/json.hpp>
#include <portaudio.h>
#include <sndfile.h>
#include <queue>
#include <mutex>
#include <csignal>
#include <condition_variable>
#include "../include/whisper.h"
#include "../ggml/include/ggml.h"



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


#define BEMO ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL)


// Global flag to control the execution loop
atomic<bool> running(true);
bool recording = false;
whisper_context *ctx = nullptr;
string recordedAudioFile = "recorded_audio.wav";
std::queue<nlohmann::json> jsonQueue;
std::mutex queueMutex;
std::condition_variable queueCondition;
std::atomic<bool> isWriting(true); 
int c = 0;
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

    // Configure input parameters
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


std::mutex fileMutex;

void saveToJson(const std::string& rawLine, const std::string& cleanedLine, const std::string& classification,
                double start_time, double end_time, int c) {
    std::lock_guard<std::mutex> lock(fileMutex);

    std::ofstream outFile("transcriptions.json", std::ios::app);
    if (!outFile.is_open()) {
        std::cerr << "Failed to open JSON file for writing.\n";
        return;
    }

    nlohmann::json event;
    event["raw_text"] = rawLine;
    event["cleaned_text"] = cleanedLine;
    event["classification"] = classification;
    event["start_time"] = start_time;
    event["end_time"] = end_time;

    outFile << event.dump(4) << ",";
    outFile.close();
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

/*----------------------------read .wavvv--------------------*/
void executeMainCommand(const string &wavFile)
{
    c++;
    string command = "./main -m ./models/ggml-base.en.bin -f " + wavFile + " -t 8";
    FILE *pipe = popen(command.c_str(), "r");
    if (!pipe)
    {
        cerr << "Failed to run the main command." << "\n";
        return;
    }
        // cout<<"lllllllllllllllll : "<<c<<" " <<rawLine<<endl;


    char buffer[1024];
    double current_time = 0.0;    
    const double step_size = 5.0; // 5 seconds for every event
    while (fgets(buffer, sizeof(buffer), pipe) != NULL)
    {
        string line(buffer);
        // cout<<"samsepi0l:---------------> "<<fgets(buffer, sizeof(buffer), pipe)<<endl;
        string rawLine = line; 
        transform(line.begin(), line.end(), line.begin(), ::tolower);
        string cleanedLine = cleanText(rawLine);

        string classification = classifyEvent(line,c);

        double start_time = current_time;
        double end_time = current_time + step_size;

        saveToJson(rawLine, cleanedLine, classification, start_time, end_time,c);

        current_time = end_time;
        // cout<<"samsepi0l:---------------> "<<fgets(buffer, sizeof(buffer), pipe)<<endl;

        cout << "Processed transcription: " << cleanedLine << "\n";
        clearJsonFileIfExceedsSize();
        
    }
    // cout << "Finalized transcriptions.json" << "\n";

    // ofstream outFile("transcriptions.json", ios_base::app);
    // outFile << "]";
    // outFile.close();
    pclose(pipe);

}

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
int main() {
    // Initialize Whisper model
whisper_context_params ctx_params = whisper_context_default_params();
whisper_context* ctx = whisper_init_from_file_with_params("models/ggml-base.en.bin", ctx_params);
    if (!ctx) {
        std::cerr << "Failed to initialize Whisper model.\n";
        return 1;
    }

    initializeJsonFile();  // Start JSON logging

    processRealTimeAudio(ctx);  // Process real-time audio

    finalizeJsonFile();  // Finalize JSON logging

    whisper_free(ctx);  // Free Whisper resources
    return 0;
}





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

