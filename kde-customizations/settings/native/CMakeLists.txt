cmake_minimum_required(VERSION 3.25)
project(FlausenSettings LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_AUTOMOC ON)
find_package(Qt6 REQUIRED COMPONENTS Quick Qml DBus)
qt_policy(SET QTP0001 NEW)
find_package(KF6KCMUtils REQUIRED)
find_package(KF6CoreAddons REQUIRED)
find_package(KF6I18n REQUIRED)
find_package(KF6WindowSystem REQUIRED)
qt_add_qml_module(flausensettings
    URI Flausen.Settings
    VERSION 1.0
    OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/Flausen/Settings"
    SOURCES kcmhost.h kcmhost.cpp timedate.h timedate.cpp windowframe.h windowframe.cpp picturepicker.h picturepicker.cpp
)
target_link_libraries(flausensettings PRIVATE Qt6::Quick Qt6::Qml Qt6::DBus KF6::KCMUtilsQuick KF6::CoreAddons KF6::WindowSystem KF6::I18n)
set_target_properties(flausensettings PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/Flausen/Settings" BUILD_RPATH "$ORIGIN" INSTALL_RPATH "$ORIGIN")
set_target_properties(flausensettingsplugin PROPERTIES BUILD_RPATH "$ORIGIN" INSTALL_RPATH "$ORIGIN")
