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
    # If you need file system support
    "joltwallet/littlefs",
    # For JSON processing if needed
    "espressif/jsmn",
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
        f.write("dependencies:\n")
        for component in COMPONENTS:
            component_parts = component.split("/")
            if len(component_parts) > 1:
                f.write(f"  {component_parts[0]}/{component_parts[1]}:\n")
            else:
                f.write(f"  {component}:\n")
            f.write(f'    version: "*"\n')
    print(f"Created component manifest file: {manifest_file}")
