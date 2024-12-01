//
//    بِسْمِ اللَّـهِ الرَّحْمَـٰنِ الرَّحِيمِ
//
/////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cstdio>
#include <thread>
#include <atomic>
#include <regex>
#include <cstring>
#include <nlohmann/json.hpp>
#include <portaudio.h>
#include <sndfile.h>
#include <queue>
#include <mutex>
#include <csignal>
#include <condition_variable>
#include "common-sdl.h"
#include "common.h"
#include "whisper.h"
#include <fstream>
#include <cassert>
#include <vector>
#include <ctime>
#include <bits/stdc++.h>
#define SAMPLE_RATE 44100
#define NUM_CHANNELS 1
#define FRAMES_PER_BUFFER 512
using json = nlohmann::json;
using namespace std;

string cleanText(const string &input);
string classifyEvent(const string &line, int c);
void clearJsonFileIfExceedsSize();
void removeClosingBracket();
void saveToJson(const string& rawLine, const string& cleanedLine, const string& classification, double start_time, double end_time, int c);
void jsonWriterThread(const string &filename);
void executeMainCommand(const string &wavFile);
void executeMainCommand(const string &wavFile);
bool compare(const nlohmann::json &a, const nlohmann::json &b);

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

            Hi!
            Give me a Hug, I will not let you go.
*/


#define BEMO ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL)


atomic<bool> running(true);
bool recording = false;
whisper_context *ctx = nullptr;
string recordedAudioFile = "recorded_audio.wav";
queue<nlohmann::json> jsonQueue;
mutex queueMutex;
condition_variable queueCondition;
atomic<bool> isWriting(true); 
int c = 0;
void trimSilence(vector<int16_t>& audioBuffer, int silenceThreshold = 200);
vector<float> resampleAudio(const vector<int16_t>& input, int inputRate, int outputRate);
string processAudioChunk(whisper_context* ctx, const float* audioData, size_t length);
void finalizeJsonFile();
void initializeJsonFile();

/*--------------------compare function for sorting---------------------- */
bool compare(const nlohmann::json &a, const nlohmann::json &b) {
    return a["start_time"] < b["start_time"];
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
string classifyEvent(const string &line,int /*c*/)
{


    //cout<<"lllllllllllllllll : "<<c<<" " <<line<<"\n";
    if (line.find("bemo") != string::npos ||
        line.find("bmo") != string::npos ||
        line.find("bimo") != string::npos ||
        line.find("vemo") != string::npos ||
        line.find("vimo") != string::npos ||
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
    ofstream outFile("transcriptions.json");
    outFile << "[";  // Start the JSON array
    outFile.close();
}
/*---------------------------------------clear json if exceeds size--------------- */
void clearJsonFileIfExceedsSize()
{
    const long long MAX_SIZE = 50 * 1024 * 1024; // limit size json file to 50 MB
    ifstream inFile("transcriptions.json", ios::ate | ios::binary);
    if (inFile.tellg() >= MAX_SIZE)
    {
        inFile.close();
        ofstream outFile("transcriptions.json", ios::trunc);
        outFile.close();
        // cout << "Cleared transcriptions.json as it exceeded 50 MB" << "\n";
        printf("Cleared transcriptions.json as it exceeded 50 MB\n");
        initializeJsonFile();

    }
    else
    {
        inFile.close();
    }
}

/*---------------------------------------close json--------------------- */
void finalizeJsonFile() {
    ifstream inFile("transcriptions.json");
    string content((istreambuf_iterator<char>(inFile)), istreambuf_iterator<char>());
    inFile.close();

    // Remove trailing comma and close the JSON array
    if (!content.empty() && content.back() == ',') {
        content.pop_back();
    }

    ofstream outFile("transcriptions.json", ios::trunc);
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


mutex fileMutex;
/*---------------------------------------------Save to json file----------------*/
void saveToJson(const string& /*rawLine*/, const string& cleanedLine, const string& classification,
                double start_time, double end_time, int /*c*/) {
    lock_guard<mutex> lock(fileMutex);

    ifstream inFile("transcriptions.json");

    if (!inFile.is_open()) {
        cerr << "Failed to open JSON file for writing.\n";
        return;
    }


    string content((istreambuf_iterator<char>(inFile)), istreambuf_iterator<char>());
    inFile.close();

    // Remove the trailing closing bracket `]`
    if (!content.empty() && content.back() == ']') {
        content.pop_back();
    }

    // Remove trailing comma if present
    if (!content.empty() && content.back() == ',') {
        content.pop_back();
    }

    nlohmann::json event;
    // event["raw_text"] = rawLine;
    event["cleaned_text"] = cleanedLine;
    event["classification"] = classification;
    event["end_time"] = end_time;
    event["start_time"] = start_time;
        if (!content.empty() && content.back() != '[') {
        content += ",";
    }
    // string content((istreambuf_iterator<char>(outFile)), istreambuf_iterator<char>());
    // if (content.empty()) {
    //     cerr << "No content in the JSON file to sort." << endl;
    //     return;
    // }
    // nlohmann::json jsonArray = nlohmann::json::parse(content);


    // std::sort(jsonArray.begin(), jsonArray.end(), compare);
    content += event.dump(4);
    
    // finalizeJsonFile();
    content+="]";
        ofstream outFile("transcriptions.json", ios::trunc);
    if (!outFile.is_open()) {
        cerr << "Failed to open JSON file for writing.\n";
        return;
    }
      outFile << content;
    outFile.close();
}

/*------------------------------------------json writer thread---------------------------------------------------------- */
/*
this function writes JSON objects from a queue to a file in a thread-safe manner, ensuring proper JSON array formatting.
*/
void jsonWriterThread(const string &filename) {
    ofstream outFile(filename, ios::trunc);
    if (!outFile.is_open()) {
        cerr << "Failed to open JSON file for writing: " << filename << "\n";
        return;
    }

    outFile << "["; // Start the JSON array
    bool isFirst = true;

    while (isWriting || !jsonQueue.empty()) {
        nlohmann::json event;

        {
            unique_lock<mutex> lock(queueMutex);
            if (jsonQueue.empty() && !isWriting) {
                break;
            }
            queueCondition.wait(lock, [] { return !jsonQueue.empty() || !isWriting; });

            if (!jsonQueue.empty()) {
                event = jsonQueue.front();
                jsonQueue.pop();
            }
        }

        if (!event.is_null()) {
            lock_guard<mutex> fileLock(fileMutex);
            if (!isFirst) {
                outFile << ",";
            }
            outFile << event.dump(4); 
            isFirst = false;
        }
    }

    outFile << "]"; 
    outFile.close();
}

/*---------------------------------------------read .wavvv-----------------------------------------------------------*/
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
        // cout<<"lllllllllllllllll : "<<c<<" " <<rawLine<<"\n";


    char buffer[1024];
    double current_time = 0.0;    
    const double step_size = 5.0; // 5 seconds for every event
    while (fgets(buffer, sizeof(buffer), pipe) != NULL)
    {
        string line(buffer);
        // cout<<"samsepi0l:---------------> "<<fgets(buffer, sizeof(buffer), pipe)<<"\n";
        string rawLine = line; 
        transform(line.begin(), line.end(), line.begin(), ::tolower);
        string cleanedLine = cleanText(rawLine);

        string classification = classifyEvent(line,c);

        double start_time = current_time;
        double end_time = current_time + step_size;

        saveToJson(rawLine, cleanedLine, classification, start_time, end_time,c);

        current_time = end_time;
        // cout<<"samsepi0l:---------------> "<<fgets(buffer, sizeof(buffer), pipe)<<"\n";

        //cout << "Processed transcription: " << cleanedLine << "\n";
        printf("Processed transcription: %s\n", cleanedLine.c_str());
        clearJsonFileIfExceedsSize();
        
    }
    // cout << "Finalized transcriptions.json" << "\n";

    // ofstream outFile("transcriptions.json", ios_base::app);
    // outFile << "]";
    // outFile.close();
    pclose(pipe);

}
/* ----------------------------------------------list audio devices (this for testing) ------------------------*/

// void listAudioDevices() {
//     PaError err = Pa_Initialize();
//     if (err != paNoError) {
//         cerr << "Failed to initialize PortAudio: " << Pa_GetErrorText(err) << "\n";
//         return;
//     }

//     int numDevices = Pa_GetDeviceCount();
//     if (numDevices < 0) {
//         cerr << "Error getting device count: " << Pa_GetErrorText(numDevices) << "\n";
//         Pa_Terminate();
//         return;
//     }

//     cout << "Available Audio Devices:" << "\n";
//     for (int i = 0; i < numDevices; ++i) {
//         const PaDeviceInfo *deviceInfo = Pa_GetDeviceInfo(i);
//         cout << "ID: " << i << ", Name: " << deviceInfo->name
//                   << ", Default Sample Rate: " << deviceInfo->defaultSampleRate << " Hz" << "\n";
//     }

//     Pa_Terminate();
// }




// command-line parameters
struct AudioData {
    std::vector<float> buffer;
    size_t maxFrames;
    size_t frameIndex;
};
struct whisper_params {
    int32_t n_threads  = min(4, (int32_t) thread::hardware_concurrency());
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

    string language  = "en";
    string model     = "models/ggml-base.en.bin";
    string fname_out;
};

// static int recordCallback(const void *inputBuffer, void *outputBuffer,
//                           unsigned long framesPerBuffer,
//                           const PaStreamCallbackTimeInfo* timeInfo,
//                           PaStreamCallbackFlags statusFlags,
//                           void *userData) {
//     AudioData *data = (AudioData*)userData;
//     const float *in = (const float*)inputBuffer;
//     size_t framesToCopy = std::min(framesPerBuffer, data->maxFrames - data->frameIndex);

//     if (inputBuffer == nullptr) {
//         for (size_t i = 0; i < framesToCopy; ++i) {
//             data->buffer[data->frameIndex++] = 0.0f;
//         }
//     } else {
//         for (size_t i = 0; i < framesToCopy; ++i) {
//             data->buffer[data->frameIndex++] = *in++;
//         }
//     }

//     return (data->frameIndex >= data->maxFrames) ? paComplete : paContinue;
// }

// void recordAudio(const std::string &filename, int durationSeconds) {
//     PaError err;
//     PaStream *stream;
//     AudioData data;

//     data.maxFrames = durationSeconds * SAMPLE_RATE;
//     data.buffer.resize(data.maxFrames * NUM_CHANNELS);
//     data.frameIndex = 0;

//     err = Pa_Initialize();
//     if (err != paNoError) {
//         std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
//         return;
//     }

//     err = Pa_OpenDefaultStream(&stream,
//                                NUM_CHANNELS, // input channels
//                                0,            // output channels
//                                paFloat32,    // sample format
//                                SAMPLE_RATE,
//                                FRAMES_PER_BUFFER,
//                                recordCallback,
//                                &data);
//     if (err != paNoError) {
//         std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
//         Pa_Terminate();
//         return;
//     }

//     err = Pa_StartStream(stream);
//     if (err != paNoError) {
//         std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
//         Pa_CloseStream(stream);
//         Pa_Terminate();
//         return;
//     }

//     std::cout << "Recording for " << durationSeconds << " seconds..." << std::endl;
//     Pa_Sleep(durationSeconds * 1000);

//     err = Pa_StopStream(stream);
//     if (err != paNoError) {
//         std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
//     }

//     err = Pa_CloseStream(stream);
//     if (err != paNoError) {
//         std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
//     }

//     Pa_Terminate();

//     // Save the recorded audio to a file
//     SF_INFO sfInfo;
//     sfInfo.channels = NUM_CHANNELS;
//     sfInfo.samplerate = SAMPLE_RATE;
//     sfInfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;

//     SNDFILE *outFile = sf_open(filename.c_str(), SFM_WRITE, &sfInfo);
//     if (!outFile) {
//         std::cerr << "Error opening output file: " << sf_strerror(outFile) << std::endl;
//         return;
//     }

//     sf_write_float(outFile, data.buffer.data(), data.buffer.size());
//     sf_close(outFile);

//     std::cout << "Recording saved to " << filename << std::endl;
// }

void whisper_print_usage(int argc, char ** argv, const whisper_params & params);

static bool whisper_params_parse(int argc, char ** argv, whisper_params & params) {
    for (int i = 1; i < argc; i++) {
        string arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            whisper_print_usage(argc, argv, params);
            exit(0);
        }
        else if (arg == "-t"    || arg == "--threads")       { params.n_threads     = stoi(argv[++i]); }
        else if (                  arg == "--step")          { params.step_ms       = stoi(argv[++i]); }
        else if (                  arg == "--length")        { params.length_ms     = stoi(argv[++i]); }
        else if (                  arg == "--keep")          { params.keep_ms       = stoi(argv[++i]); }
        else if (arg == "-c"    || arg == "--capture")       { params.capture_id    = stoi(argv[++i]); }
        else if (arg == "-mt"   || arg == "--max-tokens")    { params.max_tokens    = stoi(argv[++i]); }
        else if (arg == "-ac"   || arg == "--audio-ctx")     { params.audio_ctx     = stoi(argv[++i]); }
        else if (arg == "-vth"  || arg == "--vad-thold")     { params.vad_thold     = stof(argv[++i]); }
        else if (arg == "-fth"  || arg == "--freq-thold")    { params.freq_thold    = stof(argv[++i]); }
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
/* this jsut for testing */
// int main() {
//     const string jsonFilename = "transcriptions.json";

//     // List available audio devices
//     listAudioDevices();
//     return 0;
// }


///////////////////////////////////////////////////////////////////////////////////////////////////////

/*

  1-for use wav file as input
    *uncomment the main function below and comment the main function above

  2 -for use microphone as input real time
    *comment the main function below and uncomment the main function above

  3 -for setup evverything read requirements.txt

  4- for run the code 
    *run the command below
    *g++ -std=c++17 -o stream stream.cpp -lportaudio -lpa -lfftw3 -lsndfile -ljsoncpp -lpthread
    *./stream <path_to_wav_file>
    *./stream
    or make stream
    *./stream <path_to_wav_file>
    *./stream -m ./models/ggml-base.en.bin -t 4 -c 0
    Note : 

        *-m ./models/ggml-base.en.bin is the model path
        *-t 4 is the number of threads to use during computation
        *-c 0 is the capture device ID
    
    any issue or help contact me on my email address : abdosaaed749@gmail.com 


 */

///////////////////////////////////////////////////////////////////////////////////////////////////////
/* run using wav file  */

// int main(int argc, char *argv[])
// {
//   //  BEMO;
//     if (argc < 2)
//     {
//         cerr << "Usage: " << argv[0] << " <path_to_wav_file>" << "\n";
//         return 1;
//     }
//     string wavFile = argv[1];
//         cout << "Calling finalizeJsonFile()" << "\n";

//     clearJsonFileIfExceedsSize();
//     initializeJsonFile();
//     executeMainCommand(wavFile);
////   recordAudio("recorded_audio.wav", 10); // Record for 10 seconds
//     // cout<<"heheheheheheheheheheheee\n";
//     finalizeJsonFile();
//     return 0;
// }

///////////////////////////////////////////////////////////////////////////////////////////////////////

/*------------------------------------------------run on real time ----------------------*/
int main(int argc, char ** argv) {
    //BEMO;
    whisper_params params;

    if (whisper_params_parse(argc, argv, params) == false) {
        return 1;
    }
    

    params.keep_ms   = min(params.keep_ms,   params.step_ms);
    params.length_ms = max(params.length_ms, params.step_ms);

    const int n_samples_step = (1e-3*params.step_ms  )*WHISPER_SAMPLE_RATE;
    const int n_samples_len  = (1e-3*params.length_ms)*WHISPER_SAMPLE_RATE;
    const int n_samples_keep = (1e-3*params.keep_ms  )*WHISPER_SAMPLE_RATE;
    const int n_samples_30s  = (1e-3*30000.0         )*WHISPER_SAMPLE_RATE;

    const bool use_vad = n_samples_step <= 0; // sliding window mode uses VAD

    const int n_new_line = !use_vad ? max(1, params.length_ms / params.step_ms - 1) : 1; // number of steps to print new line

    params.no_timestamps  = !use_vad;
    params.no_context    |= use_vad;
    params.max_tokens     = 0;

    // Added: Initialize the JSON file for storing results
    initializeJsonFile();

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

    vector<float> pcmf32    (n_samples_30s, 0.0f);
    vector<float> pcmf32_old;
    vector<float> pcmf32_new(n_samples_30s, 0.0f);

    vector<whisper_token> prompt_tokens;

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

    printf("[Start speaking]\n");
    fflush(stdout);

    //  ofstream fout;
    // if (params.fname_out.length() > 0) {
    //     fout.open(params.fname_out);
    //     if (!fout.is_open()) {
    //         fprintf(stderr, "%s: failed to open output file '%s'!\n", __func__, params.fname_out.c_str());
    //         return 1;
    //     }
    // }

    // wav_writer wavWriter;
    // // save wav file
    // if (params.save_audio) {
    //     // Get current date/time for filename
    //     time_t now = time(0);
    //     char buffer[80];
    //     strftime(buffer, sizeof(buffer), "%Y%m%d%H%M%S", localtime(&now));
    //     string filename = string(buffer) + ".wav";

    //     wavWriter.open(filename, WHISPER_SAMPLE_RATE, 16, 1);
    // }

    auto t_last  = chrono::high_resolution_clock::now();
    //const auto t_start = t_last;
    double last_end_time = 0.0; 


    // main audio loop
    while (is_running) {
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

                this_thread::sleep_for(chrono::milliseconds(1));
            }

            const int n_samples_new = pcmf32_new.size();

            // take up to params.length_ms audio from previous iteration
            const int n_samples_take = min((int) pcmf32_old.size(), max(0, n_samples_keep + n_samples_len - n_samples_new));

            pcmf32.resize(n_samples_new + n_samples_take);

            for (int i = 0; i < n_samples_take; i++) {
                pcmf32[i] = pcmf32_old[pcmf32_old.size() - n_samples_take + i];
            }

            memcpy(pcmf32.data() + n_samples_take, pcmf32_new.data(), n_samples_new*sizeof(float));

            pcmf32_old = pcmf32;
        } else {
            const auto t_now  = chrono::high_resolution_clock::now();
            const auto t_diff = chrono::duration_cast<chrono::milliseconds>(t_now - t_last).count();

            if (t_diff < 2000) {
                this_thread::sleep_for(chrono::milliseconds(100));
                continue;
            }

            audio.get(2000, pcmf32_new);

            if (::vad_simple(pcmf32_new, WHISPER_SAMPLE_RATE, 1000, params.vad_thold, params.freq_thold, false)) {
                audio.get(params.length_ms, pcmf32);
            } else {
                this_thread::sleep_for(chrono::milliseconds(100));
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

            wparams.tdrz_enable      = params.tinydiarize;

            // disable temperature fallback
            wparams.temperature_inc  = params.no_fallback ? 0.0f : wparams.temperature_inc;

            wparams.prompt_tokens    = params.no_context ? nullptr : prompt_tokens.data();
            wparams.prompt_n_tokens  = params.no_context ? 0       : prompt_tokens.size();

            if (whisper_full(ctx, wparams, pcmf32.data(), pcmf32.size()) != 0) {
                fprintf(stderr, "%s: failed to process audio\n", argv[0]);
                return 6;
            }

            // Process transcription result
            {
                // double current_time = 0.0;
                const int n_segments = whisper_full_n_segments(ctx);
                for (int i = 0; i < n_segments; ++i) {
                    const char *text = whisper_full_get_segment_text(ctx, i);

                    // Retrieve the start and end times for this segment
                    // const int64_t t0 = whisper_full_get_segment_t0(ctx, i);
                    // const int64_t t1 = whisper_full_get_segment_t1(ctx, i);

                    // Convert to seconds
                    // double start_time = t0 / 100.0; // Whisper gives time in centiseconds
                    // double end_time = t1 / 100.0;

                    // // Ensure timings are consecutive if Whisper doesn't handle overlaps well
                    // if (start_time < current_time) {
                    //     start_time = current_time;
                    // }
                    // current_time = end_time;

                    // Clean and classify the text
                    printf("---------------------------> %s\n",text);
                    double start_time = last_end_time; // Set start time to last end time
                    double end_time = start_time + (whisper_full_get_segment_t1(ctx, i) - whisper_full_get_segment_t0(ctx, i)) / 100.0; // Calculate end time<
                    //cout<<"Time : "<<start_time<<" : "<<end_time<<"\n";
                    string rawLine = text; 
                    // cout<<"Debug_Text : "<<n_iter<<" " <<rawLine<<"\n";
                    transform(rawLine.begin(), rawLine.end(), rawLine.begin(), ::tolower);
                    string cleanedText = cleanText(rawLine);
                    string orgin_cleanedText = cleanText(rawLine);
                    string classification = classifyEvent(cleanedText, n_iter);
                    saveToJson(text, orgin_cleanedText, classification, start_time, end_time, n_iter);
                    last_end_time = end_time; 
                }
            }

            ++n_iter;
            if (!use_vad && (n_iter % n_new_line) == 0) {
                printf("\n");

                // keep part of the audio for next iteration to try to mitigate word boundary issues
                pcmf32_old = vector<float>(pcmf32.end() - n_samples_keep, pcmf32.end());

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
    //finalizeJsonFile();
    whisper_print_timings(ctx);
    whisper_free(ctx);

    return 0;
}
