#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "driver/gpio.h"

// Include all component headers
#include "app_config.h"
#include "display.h"
#include "FT6336U.h"
#include "main_ui.h"
#include "camera.h"
#include "sd_card.h"
#include "driver_test.h"
#include "sound_ui.h"

static const char *TAG = "main";
static display_handle_t screen; // Changed from Arduino's object to ESP-IDF compatible handle
static int setup_success = 1;

// LVGL display refresh task - replaces Arduino's loop() for GUI updates
void lvgl_display_task(void *pvParameter)
{
	while (1)
	{
		// Update the GUI
		display_update(screen);
		vTaskDelay(pdMS_TO_TICKS(5)); // Equivalent to Arduino's delay(5)
	}
}

extern "C" void app_main(void)
{
	// Initialize NVS (Non-volatile storage)
	esp_err_t ret = nvs_flash_init();
	if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
	{
		ESP_ERROR_CHECK(nvs_flash_erase());
		ret = nvs_flash_init();
	}
	ESP_ERROR_CHECK(ret);

	// Initialize serial - replaced with ESP-IDF logging
	ESP_LOGI(TAG, "Initializing...");

	// Initialize drivers
	int iic_num = wire_scan();
	int sd_init_state = sdcard_init();		   // Initialize the SD_MMC module
	int camera_init_state = camera_init_jpg(); // Initialize the camera driver
	int music_init_state = music_iis_init();   // Initialize the audio interface

	buzzer_init();			   // Initialize the buzzer
	buzzer_repeat_alert(3, 1); // Test the buzzer
	audio_init();			   // Test the audio module

	setup_success = driver_check_show(iic_num, sd_init_state, camera_init_state, music_init_state);

	if (setup_success != 0)
	{
		// Initialize display
		screen = display_init(); // Assuming a function that returns a handle to the display

		// Initialize volume
		music_set_volume(10);

		// Initialize heart rate sensor
		heartrate_init();

		// Log LVGL version - ESP-IDF style logging replaces Serial.println
		ESP_LOGI(TAG, "LVGL Version: %d.%d.%d",
				 lv_version_major(), lv_version_minor(), lv_version_patch());
		ESP_LOGI(TAG, "I am LVGL on ESP-IDF");

		// Setup UI
		setup_ui(&guider_main_ui);
		ESP_LOGI(TAG, "Setup done");

		// Create LVGL task - replaces Arduino's loop() for display updates
		xTaskCreate(lvgl_display_task, "lvgl_task", 4096, NULL, 5, NULL);
	}
	else
	{
		ESP_LOGE(TAG, "Setup failed");
	}

	// Wait for the audio test to end
	while (audio_test_isRunning())
	{
		vTaskDelay(pdMS_TO_TICKS(10));
	}

	// If we're not using a separate LVGL task, we can use the main loop
	if (setup_success != 0 && xTaskGetHandle("lvgl_task") == NULL)
	{
		// Main loop - only needed if not using the separate task
		while (1)
		{
			display_update(screen);
			vTaskDelay(pdMS_TO_TICKS(5));
		}
	}
	else
	{
		// If we have a separate task for LVGL or setup failed, just keep the main task alive
		while (1)
		{
			vTaskDelay(pdMS_TO_TICKS(100));
		}
	}
}
