cmake_minimum_required(VERSION 3.10)
project(memory_manager C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Add source files
set(SOURCES
    memory_manager.c
    test_memory_manager.c
)

# Create executable
add_executable(memory_manager_test ${SOURCES})

# Add include directory
target_include_directories(memory_manager_test PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Link against pthread library
find_package(Threads REQUIRED)
target_link_libraries(memory_manager_test PRIVATE Threads::Threads) 