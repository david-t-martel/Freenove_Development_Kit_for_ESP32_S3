import os

# Updated component list based on project requirements
COMPONENTS = [
    "lvgl",
    "esp32-camera",
    "esp-dsp",  # For audio processing
    "esp_littlefs",  # File system for storage
    "esp_http_client",  # For network connectivity
    "json",  # JSON parsing
    "nvs_flash",  # NVS flash storage
    "sdmmc",  # SD card support
    "esp_adc",  # ADC support
    "esp_timer",  # Timer functionality
]

# Create components directory structure if it doesn't exist
components_dir = os.path.join(os.environ.get("PROJECT_DIR", "."), "components")
if not os.path.exists(components_dir):
    os.makedirs(components_dir)
    print(f"Created components directory: {components_dir}")

# Create a manifest file for component manager
manifest_file = os.path.join(os.environ.get("PROJECT_DIR", "."), "idf_component.yml")
if not os.path.exists(manifest_file):
    with open(manifest_file, "w") as f:
        f.write("dependencies:\n")
        for component in COMPONENTS:
            f.write(f"  {component}:\n")
            f.write("    version: '*'\n")
    print(f"Created component manifest file: {manifest_file}")
