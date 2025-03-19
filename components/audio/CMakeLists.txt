
idf_component_register(
    SRCS
        "audio.cpp"
        "buzzer.cpp"
    INCLUDE_DIRS "include"
    REQUIRES driver esp_dsp
)
