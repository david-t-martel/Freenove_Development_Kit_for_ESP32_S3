# Architecture Overview

# TODO: Complete proposed final architecture of the project.
# TODO: Generate component CMakeLists.txt files for each component.

## Project Structure

The project is organized into several directories and files, each serving a specific purpose. Below is a high-level overview of the project structure:

```
project/
├── CMakeLists.txt                  # Main project CMake file
├── sdkconfig                       # ESP-IDF configuration
├── sdkconfig.defaults              # Default configuration values
├── idf_component.yml               # Component manager manifest
├── partitions.csv                  # Custom partition table
├── platformio.ini                  # PlatformIO configuration
│
├── main/                           # Main application code
│   ├── CMakeLists.txt
│   ├── main.c                      # Entry point (app_main)
│   └── include/
│       └── app_config.h            # Global application configuration
│
├── components/                     # Custom components
│   ├── display/                    # Display driver component
│   │   ├── CMakeLists.txt
│   │   ├── display.c
│   │   └── include/
│   │       └── display.h
│   │
│   ├── ft6336u/                    # Touch controller component
│   │   ├── CMakeLists.txt
│   │   ├── FT6336U.c
│   │   └── include/
│   │       └── FT6336U.h
│   │
│   ├── main_ui/                    # Main UI component
│   │   ├── CMakeLists.txt
│   │   ├── main_ui.c
│   │   ├── ui_helpers.c
│   │   └── include/
│   │       ├── main_ui.h
│   │       └── ui_helpers.h
│   │
│   ├── camera/                     # Camera functionality
│   │   ├── CMakeLists.txt
│   │   ├── camera.c
│   │   └── include/
│   │       └── camera.h
│   │
│   ├── sd_card/                    # SD card operations
│   │   ├── CMakeLists.txt
│   │   ├── sd_card.c
│   │   └── include/
│   │       └── sd_card.h
│   │
│   ├── audio/                      # Audio system
│   │   ├── CMakeLists.txt
│   │   ├── audio.c
│   │   ├── buzzer.c
│   │   └── include/
│   │       ├── audio.h
│   │       └── buzzer.h
│   │
│   ├── heartrate/                  # Heart rate sensor
│   │   ├── CMakeLists.txt
│   │   ├── heartrate.c
│   │   └── include/
│   │       └── heartrate.h
│   │
│   ├── driver_test/                # Hardware drivers testing
│   │   ├── CMakeLists.txt
│   │   ├── driver_test.c
│   │   └── include/
│   │       └── driver_test.h
│   │
│   ├── sound_ui/                   # Sound UI component
│   │   ├── CMakeLists.txt
│   │   ├── sound_ui.c
│   │   └── include/
│   │       └── sound_ui.h
│   │
│   └── utils/                      # Utility functions
│       ├── CMakeLists.txt
│       ├── utils.c
│       └── include/
│           └── utils.h
│
├── managed_components/             # Components managed by IDF component manager
│   ├── lvgl__lvgl/                 # LVGL library
│   ├── espressif__esp32-camera/    # ESP32 camera driver
│   └── ... (other managed components)
│
├── assets/                         # Static assets
│   ├── fonts/                      # Font files
│   ├── images/                     # Image resources
│   └── sounds/                     # Audio files
│
└── tools/                          # Build and utility scripts
    └── configure_esp_idf_components.py
```

## Code Structure

### Task Management

The application uses FreeRTOS tasks for concurrent operations:

- Display Task: Updates LVGL UI at regular intervals (5-10ms)
- Touch Task: Handles touch input processing
- Camera Task: Handles camera capture and processing
- Audio Task: Manages audio playback
- Heart Rate Task: Processes heart rate sensor data
- Main App Task: Coordinates application logic

### Communications Architecture

I2C Bus: For touch controller, sensors (configurable pins)
SPI Bus: For display communication
I2S Bus: For audio output
SDMMC Interface: For SD card access
Camera Interface: Using dedicated DCMI pins

### Memory Management

PSRAM usage for frame buffers and audio buffers
Static allocation for UI elements to minimize fragmentation
DMA usage for efficient data transfers

### Data Flow

1. User interacts with touch screen → Touch event captured → UI updated
2. Camera captures images → Image processed → Displayed on screen/saved to SD
3. Heart rate sensor reads data → Data processed → Displayed on UI
4. Audio playback requested → Audio data read → Output via I2S
