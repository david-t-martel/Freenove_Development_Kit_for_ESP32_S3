
idf_component_register(
    SRCS
        "main_ui.cpp"
        "ui_helpers.cpp"
    INCLUDE_DIRS "include"
    REQUIRES lvgl display camera sd_card audio heartrate
)
