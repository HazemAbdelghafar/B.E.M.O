if (WHISPER_SDL2)
    # stream
    set(TARGET stream)
    add_executable(${TARGET} stream.cpp)

    include_directories(..)
    include_directories(/usr/include/SDL2)

    include(DefaultTargetOptions)

    # Find sndfile library
    find_package(SndFile REQUIRED)

    target_link_libraries(${TARGET} PRIVATE common common-sdl whisper ${CMAKE_THREAD_LIBS_INIT} SndFile::sndfile)
endif ()

