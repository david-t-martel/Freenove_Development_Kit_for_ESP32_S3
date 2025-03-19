
idf_component_register(
    SRCS "FT6336U.cpp"
    INCLUDE_DIRS "include"
    REQUIRES driver esp_lcd_touch i2c_manager
)
