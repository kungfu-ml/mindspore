project(nnacl)

set(NNACL_DIR ${CMAKE_CURRENT_SOURCE_DIR})
include_directories(NNACL_DIR)

if (PLATFORM_ARM32 OR PLATFORM_ARM64)
    if ("${CMAKE_BUILD_TYPE}" STREQUAL "Release")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -fomit-frame-pointer -fstrict-aliasing -ffunction-sections -fdata-sections -ffast-math")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -fomit-frame-pointer -fstrict-aliasing -ffunction-sections -fdata-sections -ffast-math")
    endif()
endif ()

########################### files ###########################
file(GLOB KERNEL_SRC
    ${NNACL_DIR}/*.c
    ${NNACL_DIR}/fp32/*.c
    ${NNACL_DIR}/int8/*.c
    ${NNACL_DIR}/quantization/*.c
)

if (SUPPORT_TRAIN)
    file (GLOB TRAIN_SRC ${NNACL_DIR}/fp32_grad/*.c)
endif()

if (PLATFORM_ARM64)
    file(GLOB ASSEMBLY_SRC ${NNACL_DIR}/assembly/arm64/*.S)
    set_property(SOURCE ${ASSEMBLY_SRC} PROPERTY LANGUAGE C)
endif()

if (PLATFORM_ARM32)
    file(GLOB ASSEMBLY_SRC ${NNACL_DIR}/assembly/arm32/*.S)
    set_property(SOURCE ${ASSEMBLY_SRC} PROPERTY LANGUAGE C)
endif()

########################### build nnacl static library ########################
string(REPLACE "-fvisibility=hidden" "-fvisibility=default" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
add_library(nnacl STATIC ${KERNEL_SRC} ${TRAIN_SRC} ${ASSEMBLY_SRC})

########################### arm64 build optimize library ########################
if (PLATFORM_ARM64)
    add_subdirectory(${NNACL_DIR}/optimize)
endif()