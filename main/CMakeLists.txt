
idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS "include"
    REQUIRES display ft6336u main_ui camera sd_card audio heartrate driver_test sound_ui utils lvgl esp32-camera
)
