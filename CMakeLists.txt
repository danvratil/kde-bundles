cmake_minimum_required(VERSION 3.0)

include(CMakeParseArguments)

set(KF5_SDK "org.kde.KF5.Sdk")
set(KF5_PLATFORM "org.kde.KF5.Platform")
set(KF5_SDK_VERSION "5.9.0")




macro(parseSPECFile package specFile sourcesList depsList)
    execute_process(COMMAND ${CMAKE_COMMAND} -E echo_append "-- Parsing SPEC file for package ${package}")
    # The path must be relative - we use it as both target name and actual file path,
    # but absolute paths differ here and in chroot in build.sh
    execute_process(COMMAND rpmspec -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -D "dist .sdk" -q ${specFile} --qf "%{NAME}=packages/RPMS/%{ARCH}/%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm;"
                    OUTPUT_VARIABLE rawProvidesList)
    execute_process(COMMAND rpmspec -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -D "dist .sdk" -q ${specFile} --buildrequires
                    OUTPUT_VARIABLE rawBuildRequiresList)
#    execute_process(COMMAND rpmspec -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -D "dist .sdk" -q ${specFile} --requires
#                    OUTPUT_VARIABLE rawRequiresList)
    execute_process(COMMAND rpmspec -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -D "dist .sdk" -P ${specFile}
                    OUTPUT_VARIABLE parsedFile)

    foreach(provides ${rawProvidesList})
        STRING(REGEX MATCH "^([0-9a-zA-Z_-]+)=(.*)$" match ${provides})
        set(${CMAKE_MATCH_1}_target ${CMAKE_MATCH_2})
        LIST(APPEND ${package}_targets ${CMAKE_MATCH_1})
    endforeach()

    STRING(REGEX REPLACE ";" "\\\\;" rawBuildRequiresList "${rawBuildRequiresList}")
    STRING(REGEX REPLACE "\n" ";" buildRequiresList "${rawBuildRequiresList}")
    LIST(APPEND ${depsList} ${buildRequiresList})

#    STRING(REGEX REPLACE ";" "\\\\;" rawRequiresList "${rawRequiresList}")
#    STRING(REGEX REPLACE "\n" ";" requiresList "${rawRequiresList}")
#    LIST(APPEND ${depsList} ${requiresList})

    STRING(REGEX REPLACE ";" "\\\\;" parsedFile "${parsedFile}")
    STRING(REGEX REPLACE "\n" ";" parsedFile "${parsedFile}")
    foreach(line ${parsedFile})
        STRING(REGEX MATCHALL "^Source[0-9]*:(.*)$" matches "${line}")
        if (NOT "${CMAKE_MATCH_1}" STREQUAL "")
            STRING(STRIP "${CMAKE_MATCH_1}" urlStripped)
            if (${urlStripped} MATCHES "^(http|https|ftp):.*$")
                LIST(APPEND ${sourcesList} "${urlStripped}")
            endif()
        endif()
    endforeach()

    execute_process(COMMAND ${CMAKE_COMMAND} -E echo " -- done")
endmacro()


function(add_bundle)
    set(options)
    set(oneValueArgs URI PACKAGE EXECUTABLE)
    set(multiValueArgs)
    cmake_parse_arguments(BUNDLE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if ("${BUNDLE_URI}" STREQUAL "")
        message(FATAL_ERROR "Bundle URI must be specified")
    endif()
    if ("${BUNDLE_PACKAGE}" STREQUAL "")
        message(FATAL_ERROR "Bundle source RPM package name must be specified")
    endif()
    if ("${BUNDLE_EXECUTABLE}" STREQUAL "")
        message(FATAL_ERROR "Bundle main executable name must be specified")
    endif()

    add_custom_target(${BUNDLE_URI} ALL)

    set(specFile "${CMAKE_SOURCE_DIR}/packages/SPECS/${BUNDLE_PACKAGE}.spec")
    if (NOT EXISTS "${specFile}")
        message(FATAL_ERROR "SPEC file for package ${BUNDLE_PACKAGE} does not exist: ${specFile}")
    endif()

    set(sourcesList "")
    set(depsList "")
    parseSPECFile(${BUNDLE_PACKAGE} ${specFile} sourcesList depsList)

    set(sourceFiles "")
    foreach(source ${sourcesList})
        get_filename_component(fileName ${source} NAME)
        set(destFile "${CMAKE_SOURCE_DIR}/packages/SOURCES/${fileName}")
        LIST(APPEND sourceFiles ${destFile})
        LIST(FIND allDestFiles ${destFile} found)
        if (${found} EQUAL -1)
            LIST(APPEND allDestFiles ${destFile})
            add_custom_command(
                OUTPUT ${destFile}
                COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --cyan \"Downloading source for ${BUNDLE_PACKAGE}\"
                COMMAND if [ -e ${destFile} ]; then echo \"${destFile} already exists\"\; else wget ${source} -O ${destFile}\; fi
                DEPENDS ${specFile}
            )
        endif()
    endforeach()
    if ("${sourceFiles}")
        add_custom_target(${BUNDLE_URI}-sources
            DEPENDS ${destFiles}
        )
        add_dependencies(${BUNDLE_URI} ${BUNDLE_URI}-sources)
    endif()

    set(installableRPMs)
    foreach(target ${${BUNDLE_PACKAGE}_targets})
        foreach (rpm ${${target}_target})
            set(exclude FALSE)
            foreach (match IN ITEMS "-dev-" "-debuginfo-" "-static-")
                STRING(FIND "${rpm}" "${match}" pos REVERSE)
                if (${pos} GREATER -1)
                    set(exclude TRUE)
                endif()
            endforeach()
            if (NOT ${exclude})
                LIST(APPEND installableRPMs ${rpm})
            endif()
        endforeach()
    endforeach()

    set(relSpecFile "packages/SPECS/${BUNDLE_PACKAGE}.spec")
    add_custom_command(
        OUTPUT ${installableRPMs}
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI}
        COMMAND xdg-app build-init ${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI} -v ${KF5_SDK}.Var ${BUNDLE_URI} ${KF5_SDK} ${KF5_PLATFORM} ${KF5_SDK_VERSION}
        COMMAND xdg-app build ${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI} rpmbuild -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -ba ${relSpecFile}
        COMMAND xdg-app build ${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI} rpm -i ${installableRPMs}
        COMMAND xdg-app build-finish --command="${BUNDLE_EXECUTABLE}" --allow=x11 --allow=host-fs --allow=homedir --allow=pulseaudio --allow=session-dbus ${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI}
        COMMAND xdg-app build-export repo ${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI}
        DEPENDS ${specFile} ${sourceFiles}
    )
    add_custom_target(${BUNDLE_URI}-build
        DEPENDS ${targets} ${installableRPMs}
    )
    add_dependencies(${BUNDLE_URI} ${BUNDLE_URI}-build)

endfunction()


add_bundle(URI org.kde.Kate
           PACKAGE kate
           EXECUTABLE "dbus-launch /self/bin/kate"
)
add_bundle(URI org.kde.GwenView
           PACKAGE gwenview
           EXECUTABLE gwenview
)
add_bundle(URI org.kde.KCalc
           PACKAGE kcalc
           EXECUTABLE kcalc
)
add_bundle(URI org.kde.Konsole
           PACKAGE konsole
           EXECUTABLE "dbus-launch konsole"
)
add_bundle(URI org.kde.Dolphin
           PACKAGE dolphin
           EXECUTABLE "dbus-launch dolphin"
)
add_bundle(URI org.kde.Ark
           PACKAGE ark
           EXECUTABLE ark
)
add_bundle(URI org.kde.Marble
           PACKAGE marble
           EXECUTABLE marble
)
