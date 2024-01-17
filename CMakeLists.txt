
cmake_minimum_required(VERSION 3.5)

project( "State Machine Framework" VERSION 1.0.0.0 )

add_subdirectory(antlr)
add_executable(smf src/main.c)
target_link_libraries(smf smf_calculator)