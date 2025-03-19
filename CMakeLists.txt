cmake_minimum_required(VERSION 3.16)

# Set ESP-IDF path if necessary (usually handled by ESP-IDF's setup script)
# set(ENV{IDF_PATH} "/path/to/esp-idf")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32s3_project)

# Add additional global settings here if needed
