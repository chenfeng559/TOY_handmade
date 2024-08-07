# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "E:/espressif/v5.1.1/esp-idf/components/bootloader/subproject"
  "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader"
  "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix"
  "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix/tmp"
  "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix/src/bootloader-stamp"
  "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix/src"
  "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "E:/WorkStation/TOY/ESP32_TOY/sample_project/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
