// ESP-IDF Core
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"

// GPIO & Peripherals
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "driver/spi_master.h"
#include "driver/ledc.h"

// Display & Graphics
#include "lvgl.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_vendor.h"

// Touch
#include "esp_lcd_touch.h"

// Camera
#include "esp_camera.h"

// SD Card
#include "driver/sdmmc_host.h"
#include "sdmmc_cmd.h"
#include "esp_vfs_fat.h"

// Audio
#include "driver/i2s.h"
#include "esp_dsp.h"

// Your custom components (replace with actual paths)
#include "display.h"
#include "FT6336U.h"
#include "main_ui.h"
#include "camera.h"
#include "sd_card.h"
#include "driver_test.h"
#include "sound_ui.h"
