#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "sdmmc_cmd.h"

// For LVGL
#include "lvgl.h"

// Include your custom headers
#include "display.h"
#include "FT6336U.h"
#include "main_ui.h"
#include "camera.h"
#include "sd_card.h"
#include "driver_test.h"
#include "sound_ui.h"

static const char *TAG = "main";
static display_handle_t screen;
static int setup_success = 1;

// LVGL display refresh task
void lvgl_display_task(void *pvParameter)
{
	while (1)
	{
		// LVGL task handler
		lv_task_handler();
		vTaskDelay(pdMS_TO_TICKS(5));
	}
}

void app_main(void)
{
	// Initialize NVS
	esp_err_t ret = nvs_flash_init();
	if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
	{
		ESP_ERROR_CHECK(nvs_flash_erase());
		ret = nvs_flash_init();
	}
	ESP_ERROR_CHECK(ret);

	// Initialize drivers
	ESP_LOGI(TAG, "Initializing peripherals...");

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
		screen = display_init();

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
	while (audio_test_isRunning())
	{
		vTaskDelay(pdMS_TO_TICKS(10));
	}

	// Main loop - this is different from Arduino's loop()
	// Instead, we use FreeRTOS tasks for ongoing processes
	while (1)
	{
		if (setup_success != 0)
		{
			// Do any periodic main task work here
			vTaskDelay(pdMS_TO_TICKS(100));
		}
		else
		{
			// Handle error state
			ESP_LOGE(TAG, "Setup failed, system in error state");
			vTaskDelay(pdMS_TO_TICKS(1000));
		}
	}
}
