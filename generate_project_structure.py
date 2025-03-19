#!/usr/bin/env python3

import os
import shutil
import sys
from pathlib import Path

# Base project directory - change this to your project path
PROJECT_ROOT = "c:/codedev/auricleinc/freenove/esp32s3"

# Source directories to look for existing files
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
LIB_DIR = os.path.join(PROJECT_ROOT, "lib")

# File extensions to consider
SOURCE_EXTENSIONS = [".c", ".cpp", ".cc"]
HEADER_EXTENSIONS = [".h", ".hpp", ".hxx"]

# Define component CMakeLists templates with support for both C and C++ files
CMAKE_TEMPLATES = {
    "main": """
idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS "include"
    REQUIRES display ft6336u main_ui camera sd_card audio heartrate driver_test sound_ui utils lvgl esp32-camera
)
""",
    "display": """
idf_component_register(
    SRCS "display.cpp"
    INCLUDE_DIRS "include"
    REQUIRES driver esp_lcd esp_lcd_touch lvgl
)
""",
    "ft6336u": """
idf_component_register(
    SRCS "FT6336U.cpp"
    INCLUDE_DIRS "include"
    REQUIRES driver esp_lcd_touch i2c_manager
)
""",
    "main_ui": """
idf_component_register(
    SRCS
        "main_ui.cpp"
        "ui_helpers.cpp"
    INCLUDE_DIRS "include"
    REQUIRES lvgl display camera sd_card audio heartrate
)
""",
    "camera": """
idf_component_register(
    SRCS "camera.cpp"
    INCLUDE_DIRS "include"
    REQUIRES esp32-camera driver esp_event
)
""",
    "sd_card": """
idf_component_register(
    SRCS "sd_card.cpp"
    INCLUDE_DIRS "include"
    REQUIRES fatfs sdmmc esptool_py driver
)
""",
    "audio": """
idf_component_register(
    SRCS
        "audio.cpp"
        "buzzer.cpp"
    INCLUDE_DIRS "include"
    REQUIRES driver esp_dsp
)
""",
    "heartrate": """
idf_component_register(
    SRCS "heartrate.cpp"
    INCLUDE_DIRS "include"
    REQUIRES driver esp_adc esp_dsp
)
""",
    "driver_test": """
idf_component_register(
    SRCS "driver_test.cpp"
    INCLUDE_DIRS "include"
    REQUIRES display camera sd_card audio heartrate ft6336u
)
""",
    "sound_ui": """
idf_component_register(
    SRCS "sound_ui.cpp"
    INCLUDE_DIRS "include"
    REQUIRES lvgl audio
)
""",
    "utils": """
idf_component_register(
    SRCS "utils.cpp"
    INCLUDE_DIRS "include"
    REQUIRES esp_system driver
)
""",
}

# Main project CMakeLists.txt template
MAIN_CMAKE_TEMPLATE = """
cmake_minimum_required(VERSION 3.16)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32s3_project)
"""

# Template for main.cpp
MAIN_CPP_TEMPLATE = """
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "sdmmc_cmd.h"

// Include all component headers
#include "app_config.h"
#include "display.h"
#include "FT6336U.h"
#include "main_ui.h"
#include "camera.h"
#include "sd_card.h"
#include "audio.h"
#include "buzzer.h"
#include "heartrate.h"
#include "driver_test.h"
#include "sound_ui.h"

static const char *TAG = "main";
static int setup_success = 1;

// LVGL display refresh task
void lvgl_display_task(void *pvParameter) {
    while(1) {
        // LVGL task handler
        lv_task_handler();
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

extern "C" void app_main(void) {
    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Initialize drivers
    ESP_LOGI(TAG, "Initializing peripherals...");

    int iic_num = wire_scan();
    int sd_init_state = sdcard_init();          // Initialize the SD_MMC module
    int camera_init_state = camera_init_jpg();  // Initialize the camera driver
    int music_init_state = music_iis_init();    // Initialize the audio interface

    buzzer_init();                              // Initialize the buzzer
    buzzer_repeat_alert(3, 1);                  // Test the buzzer
    audio_init();                               // Test the audio module

    setup_success = driver_check_show(iic_num, sd_init_state, camera_init_state, music_init_state);

    if (setup_success != 0) {
        // Initialize display
        display_init();

        // Initialize volume
        music_set_volume(10);

        // Initialize heart rate sensor
        heartrate_init();

        // Initialize LVGL
        lv_init();

        // Log LVGL version
        ESP_LOGI(TAG, "LVGL version %d.%d.%d", lv_version_major(), lv_version_minor(), lv_version_patch());

        // Setup UI
        setup_ui(&guider_main_ui);
        ESP_LOGI(TAG, "Setup done");

        // Create LVGL task
        xTaskCreate(lvgl_display_task, "lvgl_task", 4096, NULL, 5, NULL);
    }

    // Wait for the audio test to end
    while (audio_test_isRunning()) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    // Main loop
    while (1) {
        if (setup_success != 0) {
            // Do any periodic main task work here
            vTaskDelay(pdMS_TO_TICKS(100));
        } else {
            // Handle error state
            ESP_LOGE(TAG, "Setup failed, system in error state");
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
}
"""

# Template for app_config.h
APP_CONFIG_TEMPLATE = """
#ifndef APP_CONFIG_H
#define APP_CONFIG_H

// Display configuration
#define DISPLAY_WIDTH 320
#define DISPLAY_HEIGHT 240

// I2C configuration
#define I2C_MASTER_SDA_IO 17
#define I2C_MASTER_SCL_IO 18
#define I2C_MASTER_FREQ_HZ 400000

// Audio configuration
#define BUZZER_PIN 13

// Debugging options
#define DEBUG_LEVEL ESP_LOG_INFO

#endif // APP_CONFIG_H
"""

# Template for idf_component.yml
IDF_COMPONENT_TEMPLATE = """
dependencies:
  idf:
    version: ">=5.0.0"
  lvgl/lvgl:
    version: "^8.3.9"
  espressif/esp32-camera:
    version: "~2.0.0"
  espressif/esp_lcd_touch:
    version: "~1.0.4"
  espressif/esp_lcd:
    version: "~1.0.0"
  espressif/button:
    version: "~3.1.1"
  espressif/led_strip:
    version: "~2.0.0"
  espressif/esp-dsp:
    version: "^1.2.0"
"""

# Template for platformio.ini
PLATFORMIO_TEMPLATE = """
[env:freenove_esp32_s3_wroom]
platform = espressif32
board = esp32-s3-devkitc-1
framework = espidf
monitor_speed = 115200
monitor_filters = direct, esp32_exception_decoder
board_build.partitions = partitions.csv

; Make sure to include all the components
extra_scripts =
  pre:tools/configure_esp_idf_components.py

; Build flags for configuration
build_flags =
  -DCONFIG_LWIP_IPV6=0
  -DCONFIG_FREERTOS_HZ=1000
  ; LVGL configurations
  -DLV_CONF_INCLUDE_SIMPLE=1
  -DLV_COLOR_DEPTH=16
  -DLV_COLOR_16_SWAP=1
  ; Increase stack size for LVGL task
  -DCONFIG_LVGL_TASK_STACK_SIZE=8192
  ; SD Card configurations
  -DCONFIG_SDMMC_USE_GPIO_MATRIX=1
  ; Audio configurations
  -DCONFIG_I2S_ISR_IRAM=1
"""

# Template for partitions.csv
PARTITIONS_TEMPLATE = """
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x6000,
phy_init, data, phy,     0xf000,  0x1000,
factory,  app,  factory, 0x10000, 3M,
storage,  data, spiffs,  ,        1M,
"""

# Template for configure_esp_idf_components.py
COMPONENT_CONFIG_SCRIPT = """
Import("env")
import os

# Add ESP-IDF components that you need
COMPONENTS = [
    "lvgl/lvgl",
    "espressif/esp32-camera",
    "espressif/esp_lcd_touch",
    "espressif/esp_lcd",
    "espressif/button",
    "espressif/led_strip",
    "espressif/esp-dsp",
]

# Create components directory structure if it doesn't exist
components_dir = os.path.join(env.subst("$PROJECT_DIR"), "components")
if not os.path.exists(components_dir):
    os.makedirs(components_dir)
    print(f"Created components directory: {components_dir}")

# Create a manifest file for component manager
manifest_file = os.path.join(env.subst("$PROJECT_DIR"), "idf_component.yml")
if not os.path.exists(manifest_file):
    with open(manifest_file, "w") as f:
        f.write("dependencies:\\n")
        for component in COMPONENTS:
            component_parts = component.split('/')
            if len(component_parts) > 1:
                f.write(f"  {component_parts[0]}/{component_parts[1]}:\\n")
            else:
                f.write(f"  {component}:\\n")
            f.write(f"    version: \\"*\\"\\n")
    print(f"Created component manifest file: {manifest_file}")
"""


def find_files_recursive(name_pattern, search_dirs, extensions):
    """Search recursively for files matching name pattern with given extensions."""
    found_files = []

    for directory in search_dirs:
        if not os.path.exists(directory):
            continue

        for root, _, files in os.walk(directory):
            for file in files:
                name, ext = os.path.splitext(file)

                # Check if base name matches (ignoring extension) and extension is in our list
                if name_pattern.lower() in name.lower() and ext.lower() in [
                    ext.lower() for ext in extensions
                ]:
                    found_files.append(os.path.join(root, file))

    return found_files


def find_component_files(component_name, search_dirs):
    """Find all files related to a component."""
    source_files = []
    header_files = []

    # Normalize component name, handle special cases
    if component_name == "ft6336u":
        search_patterns = ["ft6336", "FT6336"]
    else:
        search_patterns = [component_name]

    # Find all matching source files
    for pattern in search_patterns:
        source_files.extend(
            find_files_recursive(pattern, search_dirs, SOURCE_EXTENSIONS)
        )
        header_files.extend(
            find_files_recursive(pattern, search_dirs, HEADER_EXTENSIONS)
        )

    return source_files, header_files


def copy_file_to_destination(src_file, dest_file, component):
    """Copy a file to the destination directory, create template if source is missing."""
    # Create parent directories if needed
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

    # Copy the file if it exists
    if os.path.exists(src_file):
        print(
            f"Copying {os.path.basename(src_file)} to {os.path.dirname(dest_file)} for {component} component"
        )
        shutil.copy2(src_file, dest_file)
        return True
    return False


def create_template_source_file(file_path, component, is_header=False):
    """Create a template source or header file."""
    filename = os.path.basename(file_path)

    # Create parent directories if needed
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        if is_header:
            guard = filename.upper().replace(".", "_")
            f.write(f"#ifndef {guard}\n")
            f.write(f"#define {guard}\n\n")
            f.write(f"// {filename} for {component} component\n\n")
            f.write(f"#endif // {guard}\n")
        else:
            if filename.endswith(tuple(SOURCE_EXTENSIONS[1:])):  # .cpp, .cc
                f.write(f"// {filename} for {component} component\n")
                f.write("#include <Arduino.h>\n")
                f.write(f'#include "{os.path.splitext(filename)[0]}.h"\n\n')
                f.write("// TODO: Implement component functionality\n")
            else:  # .c
                f.write(f"// {filename} for {component} component\n\n")
                f.write("// TODO: Implement component functionality\n")

    print(f"Created template {filename} for {component} component")


def create_directory_structure():
    """Create the entire directory structure."""
    print(f"Creating project structure in {PROJECT_ROOT}")

    # Create main directory structure
    dirs = [
        "main/include",
        "components",
        "assets/fonts",
        "assets/images",
        "assets/sounds",
        "tools",
        "managed_components",
    ]

    # Create component directories
    components = [
        "display",
        "ft6336u",
        "main_ui",
        "camera",
        "sd_card",
        "audio",
        "heartrate",
        "driver_test",
        "sound_ui",
        "utils",
    ]

    for component in components:
        dirs.append(f"components/{component}/include")

    # Create all directories
    for directory in dirs:
        os.makedirs(os.path.join(PROJECT_ROOT, directory), exist_ok=True)
        print(f"Created directory: {directory}")

    return components


def process_component_files(component, search_dirs):
    """Process all files for a component."""
    component_dir = os.path.join(PROJECT_ROOT, "components", component)
    include_dir = os.path.join(component_dir, "include")

    # Create CMakeLists.txt
    cmake_path = os.path.join(component_dir, "CMakeLists.txt")
    with open(cmake_path, "w") as f:
        f.write(CMAKE_TEMPLATES[component])
    print(f"Created {cmake_path}")

    # Find component source and header files
    source_files, header_files = find_component_files(component, search_dirs)

    # Special cases for components with multiple files
    if component == "audio":
        required_sources = ["audio.cpp", "buzzer.cpp"]
        required_headers = ["audio.h", "buzzer.h"]
    elif component == "main_ui":
        required_sources = ["main_ui.cpp", "ui_helpers.cpp"]
        required_headers = ["main_ui.h", "ui_helpers.h"]
    else:
        if component == "ft6336u":
            required_sources = ["FT6336U.cpp"]
            required_headers = ["FT6336U.h"]
        else:
            required_sources = [f"{component}.cpp"]
            required_headers = [f"{component}.h"]

    # Process source files
    for src_filename in required_sources:
        dest_path = os.path.join(component_dir, src_filename)

        # Try to find a matching source file
        found = False
        for src_file in source_files:
            src_basename = os.path.basename(src_file)
            src_name, _ = os.path.splitext(src_basename)
            required_name, _ = os.path.splitext(src_filename)

            # Match file by name pattern (ignoring extension)
            if src_name.lower() == required_name.lower():
                copy_file_to_destination(src_file, dest_path, component)
                found = True
                break

        # Create template if no matching file was found
        if not found:
            create_template_source_file(dest_path, component, False)

    # Process header files
    for header_filename in required_headers:
        dest_path = os.path.join(include_dir, header_filename)

        # Try to find a matching header file
        found = False
        for header_file in header_files:
            header_basename = os.path.basename(header_file)
            header_name, _ = os.path.splitext(header_basename)
            required_name, _ = os.path.splitext(header_filename)

            # Match file by name pattern (ignoring extension)
            if header_name.lower() == required_name.lower():
                copy_file_to_destination(header_file, dest_path, component)
                found = True
                break

        # Create template if no matching file was found
        if not found:
            create_template_source_file(dest_path, component, True)


def create_component_files(components):
    """Create files for all components."""
    search_dirs = [SRC_DIR, LIB_DIR]

    # Process each component
    for component in components:
        process_component_files(component, search_dirs)


def create_main_files():
    """Create main project files."""
    # Create main CMakeLists.txt
    with open(os.path.join(PROJECT_ROOT, "CMakeLists.txt"), "w") as f:
        f.write(MAIN_CMAKE_TEMPLATE)
    print("Created main CMakeLists.txt")

    # Create main component CMakeLists.txt
    with open(os.path.join(PROJECT_ROOT, "main", "CMakeLists.txt"), "w") as f:
        f.write(CMAKE_TEMPLATES["main"])
    print("Created main component CMakeLists.txt")

    # Search for main source files
    main_candidates = find_files_recursive("main", [SRC_DIR], SOURCE_EXTENSIONS)
    sketch_candidates = find_files_recursive("sketch", [SRC_DIR], SOURCE_EXTENSIONS)
    all_candidates = main_candidates + sketch_candidates

    # Create main.cpp
    main_path = os.path.join(PROJECT_ROOT, "main", "main.cpp")
    if all_candidates and copy_file_to_destination(
        all_candidates[0], main_path, "main"
    ):
        print(f"Using existing main file: {os.path.basename(all_candidates[0])}")
    else:
        with open(main_path, "w") as f:
            f.write(MAIN_CPP_TEMPLATE)
        print("Created template main.cpp")

    # Create app_config.h
    config_path = os.path.join(PROJECT_ROOT, "main", "include", "app_config.h")
    config_candidates = find_files_recursive(
        "config", [SRC_DIR, LIB_DIR], HEADER_EXTENSIONS
    )
    app_config_candidates = find_files_recursive(
        "app_config", [SRC_DIR, LIB_DIR], HEADER_EXTENSIONS
    )
    all_config_candidates = config_candidates + app_config_candidates

    if all_config_candidates and copy_file_to_destination(
        all_config_candidates[0], config_path, "app_config"
    ):
        print(
            f"Using existing config file: {os.path.basename(all_config_candidates[0])}"
        )
    else:
        with open(config_path, "w") as f:
            f.write(APP_CONFIG_TEMPLATE)
        print("Created template app_config.h")

    # Create other project files using existing templates
    create_project_config_files()


def create_project_config_files():
    """Create project configuration files."""
    # Create idf_component.yml
    with open(os.path.join(PROJECT_ROOT, "idf_component.yml"), "w") as f:
        f.write(IDF_COMPONENT_TEMPLATE)
    print("Created idf_component.yml")

    # Create platformio.ini
    with open(os.path.join(PROJECT_ROOT, "platformio.ini"), "w") as f:
        f.write(PLATFORMIO_TEMPLATE)
    print("Created platformio.ini")

    # Create partitions.csv
    with open(os.path.join(PROJECT_ROOT, "partitions.csv"), "w") as f:
        f.write(PARTITIONS_TEMPLATE)
    print("Created partitions.csv")

    # Create the ESP-IDF components configuration script
    with open(
        os.path.join(PROJECT_ROOT, "tools", "configure_esp_idf_components.py"), "w"
    ) as f:
        f.write(COMPONENT_CONFIG_SCRIPT)
    print("Created configure_esp_idf_components.py")


def main():
    print("Starting ESP32-S3 project structure generation...")

    # Check if project root exists
    if not os.path.exists(PROJECT_ROOT):
        print(f"Error: Project root {PROJECT_ROOT} does not exist.")
        sys.exit(1)

    # Check if source directories exist
    if not os.path.exists(SRC_DIR):
        print(f"Warning: Source directory {SRC_DIR} does not exist.")

    if not os.path.exists(LIB_DIR):
        print(f"Warning: Library directory {LIB_DIR} does not exist.")

    # Create directory structure
    components = create_directory_structure()

    # Create component files
    create_component_files(components)

    # Create main project files
    create_main_files()

    print("\nProject structure created successfully!")
    print(f"Project located at: {PROJECT_ROOT}")
    print("\nNext steps:")
    print("1. Review the imported files and fix any integration issues")
    print("2. Update CMakeLists.txt files if needed for any additional dependencies")
    print("3. Configure your specific hardware settings in app_config.h")
    print("4. Build the project with PlatformIO using ESP-IDF framework")


if __name__ == "__main__":
    main()
