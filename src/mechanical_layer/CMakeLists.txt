cmake_minimum_required(VERSION 3.9)
project(CrowdMechanics VERSION 1.0.1 DESCRIPTION "The Crowd mechanics library")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
include(GNUInstallDirs)
add_library(CrowdMechanics
        src/Agent.cpp
        src/Crowd.cpp
        src/MechanicalLayer.cpp
        src/Main.cpp
        src/Global.cpp
        src/InputStatic.cpp
        3rdparty/tinyxml/tinyxml2.cpp)
set_target_properties(CrowdMechanics PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    PUBLIC_HEADER api/CrowdMechanics.h
    CXX_STANDARD 20)
if (NOT MSVC)
    SET (CMAKE_CXX_FLAGS "-Wall -Wextra -O3")
endif ()

target_include_directories(CrowdMechanics PRIVATE include 3rdparty/tinyxml)
configure_file(CrowdMechanics.pc.in CrowdMechanics.pc @ONLY)

install(TARGETS CrowdMechanics
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES ${CMAKE_BINARY_DIR}/mylib.pc
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/pkgconfig)
