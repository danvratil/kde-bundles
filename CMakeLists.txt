cmake_minimum_required(VERSION 3.0)

include(CMakeParseArguments)

set(KF5_SDK "org.kde.KF5.Sdk")
set(KF5_PLATFORM "org.kde.KF5.Platform")
set(KF5_SDK_VERSION "5.9.0")




function(parseSPECFile package specFile sourcesList allRPMs)
    execute_process(COMMAND ${CMAKE_COMMAND} -E echo_append "-- Parsing SPEC file for package ${package}")
    # The path must be relative - we use it as both target name and actual file path,
    # but absolute paths differ here and in chroot in build.sh
    execute_process(COMMAND rpmspec -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -D "dist .sdk" -q ${specFile} --qf "packages/RPMS/%{ARCH}/%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm;"
                    OUTPUT_VARIABLE rawRPMsList)
    execute_process(COMMAND rpmspec -D "_topdir ${CMAKE_SOURCE_DIR}/packages" -D "dist .sdk" -P ${specFile}
                    OUTPUT_VARIABLE parsedFile)

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

    set(${allRPMs} ${rawRPMsList} PARENT_SCOPE)
    set(${sourcesList} ${${sourcesList}} PARENT_SCOPE)
endfunction()


function(getSources specFile allSources urls sourceFiles)
    set(newSourceFiles)
    foreach(sourceUrl ${urls})
        get_filename_component(fileName ${sourceUrl} NAME)
        set(sourceFile "${CMAKE_SOURCE_DIR}/packages/SOURCES/${fileName}")
        LIST(APPEND ${sourceFiles} ${sourceFile})
        LIST(FIND allSources ${sourceFile} found)
        if (${found} EQUAL -1)
            LIST(APPEND allSources ${sourceFile})
            add_custom_command(
                OUTPUT ${sourceFile}
                COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --cyan \"Downloading source for ${specFile}\"
                COMMAND if [ -e ${sourceFile} ]; then echo \"${sourceFile} already exists\"\; else wget ${sourceUrl} -O ${sourceFile}\; fi
                DEPENDS ${specFile}
            )
        endif()
    endforeach()

    # Propagate the changes we did to allSources up
    set(allSources ${allSources} PARENT_SCOPE)
    if ("${newSourceFiles}")
        set(${sourceFiles} ${newSourceFiles} PARENT_SCOPE)
    else()
        set(${sourceFiles} "" PARENT_SCOPE)
    endif()
endfunction()


function(buildRPM builddir package uri allSources buildRPMs runtimeRPMs)
    set(specFile "${CMAKE_SOURCE_DIR}/packages/SPECS/${package}.spec")

    set(buildDeps ${buildRPMs})
    set(runtimeDeps ${runtimeRPMs})

    # Parse the SPEC file
    set(urlsList)
    set(allRPMs)
    parseSPECFile(${package} ${specFile} urlsList allRPMs)

    # Get sources
    set(sourceFiles)
    getSources(${specFile} "${allSources}" "${urlsList}" sourceFiles)
    if ("${sourceFiles}")
        add_custom_target(${package}-sources
            DEPENDS ${sourceFiles}
        )
        add_dependencies(${package} ${package}-sources)
    endif()

    # Propagate the changes to allSources even further
    set(allSources ${allSources} PARENT_SCOPE)

    set(relSpecFile "packages/SPECS/${package}.spec")
    add_custom_command(
        OUTPUT ${allRPMs}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Initializing build directory\"
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${builddir}
        COMMAND xdg-app build-init ${builddir} -v ${KF5_SDK}.Var ${uri} ${KF5_SDK} ${KF5_PLATFORM} ${KF5_SDK_VERSION}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Installing dependencies\"
        COMMAND if [ -n \"${buildDeps}${runtimeDeps}\" ]\; then xdg-app build ${builddir} rpm -i ${buildDeps} ${runtimeDeps}\; fi
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Building RPM\"
        COMMAND xdg-app build ${builddir} rpmbuild -D \"_topdir ${CMAKE_SOURCE_DIR}/packages\" -ba ${relSpecFile}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Cleaning up build directory\"
        DEPENDS ${specFile} ${sourceFiles} ${buildDeps} ${runtimeDeps}
    )

    add_custom_target(${package}-build
           DEPENDS ${allRPMs}
    )
    add_dependencies(${package} ${package}-build)

    # Split runtime and devel packages
    foreach(rpm ${allRPMs})
        set(dest "RUNTIME")
        # Completely ignore debuginfos
        foreach (match IN ITEMS "-dev-" "-static-" "-debuginfo-" "-utils-" "-samples-" "-examples-")
            STRING(FIND "${rpm}" "${match}" pos REVERSE)
            if (${pos} GREATER -1)
                if (${match} STREQUAL "-debuginfo-" OR ${match} STREQUAL "-utils-" OR
                    ${match} STREQUAL "-samples-" OR ${match} STREQUAL "-examples-")
                    set(dest "EXCLUDE")
                    break()
                elseif (${match} STREQUAL "-dev-" OR ${match} STREQUAL "-static-")
                    set(dest "DEVEL")
                    break()
                else()
                    set(dest "RUNTIME")
                    break()
                endif()
            endif()
        endforeach()
        if (${dest} STREQUAL "DEVEL")
            LIST(APPEND buildDeps ${rpm})
        elseif (${dest} STREQUAL "RUNTIME")
            LIST(APPEND runtimeDeps ${rpm})
        else()
            # Exclude
        endif()
    endforeach()

    set(buildRPMs ${buildDeps} PARENT_SCOPE)
    set(runtimeRPMs ${runtimeDeps} PARENT_SCOPE)
endfunction()


function(createAndExportBundle uri rpms executable privileges)
    set(arguments "")
    foreach (priv ${privileges})
        if ("${priv}" STREQUAL "SESSION_DBUS")
            set(arguments ${arguments} --allow=session-dbus)
        elseif ("${priv}" STREQUAL "SYSTEM_DBUS")
            set(arguments ${arguments} --allow=system-dbus)
        elseif ("${priv}" STREQUAL "PULSEAUDIO")
            set(arguments ${arguments} --allow=pulseaudio)
        elseif ("${priv}" STREQUAL "X11")
            set(arguments ${arguments} --allow=x11)
        elseif ("${priv}" STREQUAL "WAYLAND")
            set(arguments ${arguments} --allow=wayland)
        elseif ("${priv}" STREQUAL "NETWORK")
            set(arguments ${arguments} --allow=network)
        elseif ("${priv}" STREQUAL "HOMEDIR")
            set(arguments ${arguments} --allow=homedir)
        elseif ("${priv}" STREQUAL "HOSTFS")
            set(arguments ${arguments} --allow=host-fs)
        elseif ("${priv}" STREQUAL "DRI")
            set(arguments ${arguments} --allow=dri)
        elseif ("${priv}" STREQUAL "IPC")
            set(arguments ${arguments} --allow=ipc)
        else ()
            message(FATAL_ERROR "Unknown privileges: ${priv}")
        endif()
    endforeach()

    set(builddir "${CMAKE_SOURCE_DIR}/build/${uri}")
    add_custom_command(
        TARGET ${uri} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Preparing builddir for export\"
        COMMAND xdg-app build-init ${builddir} -v ${KF5_SDK}.Var ${uri} ${KF5_SDK} ${KF5_PLATFORM} ${KF5_SDK_VERSION}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Installing packages into builddir\"
        COMMAND xdg-app build ${builddir} rpm -i ${rpms}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Finishing build and generating metadata\"
        COMMAND xdg-app build-finish --command=\"${executable}\" ${arguments} ${builddir}
        COMMAND echo \"Build ${uri}\" > ${builddir}/.COMMITMSG
        COMMAND nano ${builddir}/.COMMITMSG
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Exporting build into repository\"
        COMMAND xdg-app build-export repo ${builddir} -s \"`cat ${builddir}/.COMMITMSG`\"
        COMMAND ${CMAKE_COMMAND} -E remove ${builddir}/.COMMITMSG
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${builddir}
        DEPENDS ${specFile} ${sourceFiles}
    )
endfunction()


function(add_bundle)
    set(options)
    set(oneValueArgs URI PACKAGE EXECUTABLE)
    set(multiValueArgs DEPENDS PRIVILEGES)
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

    add_custom_target(${BUNDLE_PACKAGE})

    set(builddir "${CMAKE_SOURCE_DIR}/build/${BUNDLE_PACKAGE}")
    set(buildRPMs)
    set(runtimeRPMs)
    foreach (dep ${BUNDLE_DEPENDS})
        set(buildRPMs ${${dep}_BUILD_RPMS} ${buildRPMs})
        set(runtimeRPMs ${${dep}_RPMS} ${runtimeRPMs})
    endforeach()

    add_custom_target(${BUNDLE_URI} ALL DEPENDS ${BUNDLE_PACKAGE})
    buildRPM(${builddir} ${BUNDLE_PACKAGE} ${BUNDLE_URI} "${allSources}" "${buildRPMs}" "${runtimeRPMs}")

    createAndExportBundle(${BUNDLE_URI} "${runtimeRPMs}" ${BUNDLE_EXECUTABLE} "${BUNDLE_PRIVILEGES}")

    set(allSources ${allSources} PARENT_SCOPE)
endfunction()

function(add_package package)
    set(options)
    set(oneValueArgs)
    set(multiValueArgs DEPENDS)
    cmake_parse_arguments(PACKAGE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    add_custom_target(${package})

    set(builddir "${CMAKE_SOURCE_DIR}/build/${package}")
    set(buildRPMs)
    set(runtimeRPMs)
    foreach (dep ${PACKAGE_DEPENDS})
        set(buildRPMs ${${dep}_BUILD_RPMS} ${buildRPMs})
        set(runtimeRPMs ${${dep}_RPMS} ${runtimeRPMs})
    endforeach()
    set(allSources "")

    buildRPM(${builddir} ${package} "org.kde.tmp" "${allSources}" "${buildRPMs}" "${runtimeRPMs}")
    add_dependencies(${package} ${package}-build)

    set(allSources ${allSources} PARENT_SCOPE)

    set(${package}_RPMS ${runtimeRPMs} PARENT_SCOPE)
    set(${package}_BUILD_RPMS ${buildRPMs} PARENT_SCOPE)
endfunction()

# Packages
add_package(gsm)
add_package(libsndfile DEPENDS gsm)
add_package(libkdegames DEPENDS libsndfile)
add_package(exiv2)
add_package(LibRaw)
add_package(libkdcraw DEPENDS LibRaw)

# Bundles
add_bundle(URI org.kde.Kate
           PACKAGE kate
           EXECUTABLE kate
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR HOSTFS
)
add_bundle(URI org.kde.GwenView
           PACKAGE gwenview
           EXECUTABLE gwenview
           DEPENDS exiv2 libkdcraw
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR
)
add_bundle(URI org.kde.KCalc
           PACKAGE kcalc
           EXECUTABLE kcalc
           PRIVILEGES X11
)
add_bundle(URI org.kde.Konsole
           PACKAGE konsole
           EXECUTABLE konsole
           PRIVILEGES X11 SESSION_DBUS SYSTEM_DBUS NETWORK HOMEDIR HOSTFS IPC
)
add_bundle(URI org.kde.Dolphin
           PACKAGE dolphin
           EXECUTABLE dolphin
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR HOSTFS
)
add_bundle(URI org.kde.Ark
           PACKAGE ark
           EXECUTABLE ark
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR
)
add_bundle(URI org.kde.Marble
           PACKAGE marble
           EXECUTABLE marble-qt
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR
)
add_bundle(URI org.kde.Trojita
           PACKAGE trojita
           EXECUTABLE trojita
           PRIVILEGES X11 NETWORK HOMEDIR
)
add_bundle(URI org.kde.Bomber
           PACKAGE bomber
           EXECUTABLE bomber
           DEPENDS libkdegames
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR
)

