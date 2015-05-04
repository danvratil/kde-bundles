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

    foreach(rpm ${rawRPMsList})
        LIST(APPEND ${allRPMs} ${rpm})
    endforeach()

    STRING(REGEX REPLACE ";" "\\\\;" parsedFile "${parsedFile}")
    STRING(REGEX REPLACE "\n" ";" parsedFile "${parsedFile}")
    foreach(line ${parsedFile})
        STRING(REGEX MATCHALL "^Source[0-9]*:(.*)$" matches "${line}")
        if (NOT "${CMAKE_MATCH_1}" STREQUAL "")
            STRING(STRIP "${CMAKE_MATCH_1}" urlStripped)
            if (${urlStripped} MATCHES "^(http|https|ftp):.*$")
                LIST(APPEND sourcesList "${urlStripped}")
            endif()
        endif()
    endforeach()

    execute_process(COMMAND ${CMAKE_COMMAND} -E echo " -- done")

    set(${allRPMs} ${${allRPMs}} PARENT_SCOPE)
    set(sourcesList ${sourcesList} PARENT_SCOPE)
endfunction()


function(initBuildDir builddir package uri)
    add_custom_target(${package}-init
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green "Initializing build directory"
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${builddir}
        COMMAND xdg-app build-init ${builddir} -v ${KF5_SDK}.Var ${uri} ${KF5_SDK} ${KF5_PLATFORM} ${KF5_SDK_VERSION}
    )
endfunction()


function(getSources specFile allSources urls sourceFiles)
    foreach(sourceUrl ${urls})
        get_filename_component(fileName ${sourceUrl} NAME)
        set(sourceFile "${CMAKE_SOURCE_DIR}/packages/SOURCES/${fileName}")
        LIST(APPEND ${sourceFiles} ${destFile})
        LIST(FIND ${allSources} ${sourceFile} found)
        if (${found} EQUAL -1)
            LIST(APPEND allSources ${sourceFile})
            add_custom_command(
                OUTPUT ${sourceFile}
                COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --cyan \"Downloading source for ${BUNDLE_PACKAGE}\"
                COMMAND if [ -e ${sourceFile} ]; then echo \"${sourceFile} already exists\"\; else wget ${sourceUrl} -O ${sourceFile}\; fi
                DEPENDS ${specFile}
            )
        endif()
    endforeach()

    # Propagate the changes we did to allSources up
    set(allSources ${allSources} PARENT_SCOPE)
endfunction()


function(buildRPM builddir package allSources buildRPMs runtimeRPMs)
    set(specFile "${CMAKE_SOURCE_DIR}/packages/SPECS/${package}.spec")

    # Parse the SPEC file
    set(urlsList "")
    set(allRPMs "")
    parseSPECFile(${package} ${specFile} "${urlsList}" allRPMs)

    # Get sources
    set(sourceFiles "")
    getSources(${specFile} "${allSources}" "${urlsList}" sourceFiles)
    if ("${sourceFiles}")
        add_custom_target(${package}-sources
            DEPENDS ${sourcesFiles}
        )
        add_dependencies(${package} ${package}-sources)
    endif()

    # Propagate the changes to allSources even further
    set(allSources ${allSources} PARENT_SCOPE)

    set(relSpecFile "packages/SPECS/${package}.spec")
    add_custom_command(
        OUTPUT ${allRPMs}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green "Installing dependencies..."
        COMMAND if [ -n \"${buildRPMs}${runtimeRPMs}\" ]\; then xdg-app build ${builddir} rpm -i ${buildRPMs} ${runtimeRPMs}\; fi
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green "Building RPM..."
        COMMAND xdg-app build ${builddir} rpmbuild -D \"_topdir ${CMAKE_SOURCE_DIR}/packages\" -ba ${relSpecFile}
        DEPENDS ${builddir}/metadata ${specFile} ${sourceFiles} ${buildRPMs} ${runtimeRPMs}
    )

    add_custom_target(${package}-build
            DEPENDS ${package}-init  ${allRPMs} ${buildRPMs} ${runtimeRPMs}
    )
    add_dependencies(${package} ${package}-build)

    # Split runtime and devel packages
    foreach(rpm ${allRPMs})
        set(runtime TRUE)
        foreach (match IN ITEMS "-dev-" "-debuginfo-" "-static-")
            STRING(FIND "${rpm}" "${match}" pos REVERSE)
            if (${pos} GREATER -1)
                set(runtime FALSE)
            endif()
        endforeach()
        if (NOT ${runtime})
            LIST(APPEND buildRPMs ${rpm})
        else()
            LIST(APPEND runtimeRPMs ${rpm})
        endif()
    endforeach()

    set(buildRPMs ${buildRPMs} PARENT_SCOPE)
    set(runtimeRPMs ${runtimeRPMs} PARENT_SCOPE)
endfunction()


function(createAndExportBundle builddir uri rpms executable privileges)
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

    add_custom_command(
        TARGET ${uri} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Installing packages into builddir...\"
        COMMAND xdg-app build ${builddir} rpm -i ${rpms}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Finishing build and generating metadata...\"
        COMMAND xdg-app build-finish --command=\"${executable}\" ${arguments} ${builddir}
        COMMAND echo \"Build ${uri}\" > ${builddir}/.COMMITMSG
        COMMAND nano ${builddir}/.COMMITMSG
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Exporting build into repository...\"
        COMMAND xdg-app build-export repo ${builddir} -s \"`cat ${builddir}/.COMMITMSG`\"
        COMMAND ${CMAKE_COMMAND} -E remove ${builddir}/.COMMITMSG
        DEPENDS ${builddir}/metadata ${specFile} ${sourceFiles}
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

    # Initialize build directory
    set(builddir "${CMAKE_SOURCE_DIR}/build/${BUNDLE_PACKAGE}")
    initBuildDir(${builddir} ${BUNDLE_PACKAGE} ${BUNDLE_URI})

    # Build all dependencies
    set(buildRPMs "")
    set(runtimeRPMs "")
    foreach(dep ${BUNDLE_DEPENDS})
        add_custom_target(${dep})
        buildRPM(${builddir} ${dep} "${allSources}" "${buildRPMS}" "${runtimeRPMs}")
        add_dependencies(${BUNDLE_PACKAGE} ${buildRPMs} ${runtimeRPMs})
    endforeach()

    # Build the package itself
    add_custom_target(${BUNDLE_URI} ALL DEPENDS ${BUNDLE_PACKAGE})
    buildRPM(${builddir} ${BUNDLE_PACKAGE} "${allSources}" "${buildRPMs}" "${runtimeRPMs}")

    createAndExportBundle(${builddir} ${BUNDLE_URI} "${runtimeRPMs}" ${BUNDLE_EXECUTABLE} "${BUNDLE_PRIVILEGES}")

    set(allSources ${allSources} PARENT_SCOPE)
endfunction()


add_bundle(URI org.kde.Kate
           PACKAGE kate
           EXECUTABLE kate
           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR HOSTFS
)
add_bundle(URI org.kde.GwenView
           PACKAGE gwenview
           EXECUTABLE gwenview
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
           PRIVILEGES X11 NETWORK HOMEDIR
)
add_bundle(URI org.kde.Trojita
           PACKAGE trojita
           EXECUTABLE trojita
           PRIVILEGES X11 NETWORK HOMEDIR
)
