cmake_minimum_required(VERSION 3.5)
project(gen)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -O0 -g")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wshadow -Wconversion")

set(SOURCE_FILES a.cpp)
add_executable(gen ${SOURCE_FILES})

#target_link_libraries(gen ${Boost_LIBRARIES})
