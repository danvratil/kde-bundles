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


function(createAndExportBundle BUNDLE_URI)
    set(options)
    set(oneValueArgs)
    set(multiValueArgs RPMS)
    cmake_parse_arguments(BUNDLE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    set(builddir "${CMAKE_SOURCE_DIR}/build/${BUNDLE_URI}")
    add_custom_command(
        TARGET ${BUNDLE_URI} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Preparing builddir for export\"
        COMMAND xdg-app build-init ${builddir} -v ${KF5_SDK}.Var ${BUNDLE_URI} ${KF5_SDK} ${KF5_PLATFORM} ${KF5_SDK_VERSION}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Installing packages into builddir\"
        COMMAND xdg-app build ${builddir} rpm -i ${BUNDLE_RPMS}
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Finishing build and generating metadata\"
        COMMAND xdg-app build-finish --command=\"${BUNDLE_EXECUTABLE}\" ${builddir}
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/metadata/${BUNDLE_URI}.metadata ${builddir}/metadata
        COMMAND echo \"${BUNDLE_URI}: build\" > ${builddir}/.COMMITMSG
        COMMAND nano ${builddir}/.COMMITMSG
        COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --green \"Exporting build into repository\"
        COMMAND xdg-app build-export repo ${builddir} -b \"`cat ${builddir}/.COMMITMSG`\"
        COMMAND ${CMAKE_COMMAND} -E remove ${builddir}/.COMMITMSG
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${builddir}
        DEPENDS ${specFile} ${sourceFiles}
    )
endfunction()


function(add_bundle BUNDLE_URI)
    set(options)
    set(oneValueArgs PACKAGE)
    set(multiValueArgs DEPENDS)
    cmake_parse_arguments(BUNDLE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if ("${BUNDLE_URI}" STREQUAL "")
        message(FATAL_ERROR "Bundle URI must be specified")
    endif()
    if ("${BUNDLE_PACKAGE}" STREQUAL "")
        message(FATAL_ERROR "Bundle source RPM package name must be specified")
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

    createAndExportBundle(${BUNDLE_URI} RPMS "${runtimeRPMs}")

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
add_package(ksbinit)

add_package(gsm)
add_package(libsndfile DEPENDS gsm)
add_package(libkdegames DEPENDS libsndfile)
add_package(libkeduvocdocument)
add_package(exiv2)
add_package(LibRaw)
add_package(libkdcraw DEPENDS LibRaw)
add_package(qimageblitz)

# Bundles
add_bundle(org.kde.kate
           PACKAGE kate
           DEPENDS ksbinit
)

add_bundle(org.kde.gwenview
           PACKAGE gwenview
           DEPENDS exiv2 libkdcraw
)

add_bundle(org.kde.kcalc
           PACKAGE kcalc
           PRIVILEGES X11
)
add_bundle(org.kde.konsole
           PACKAGE konsole
)

#add_bundle(org.kde.Dolphin
#           PACKAGE dolphin
#           PRIVILEGES X11 SESSION_DBUS NETWORK HOMEDIR HOSTFS
#)
add_bundle(org.kde.ark
           PACKAGE ark
)
add_bundle(org.kde.marble
           PACKAGE marble
)
add_bundle(org.kde.trojita
           PACKAGE trojita
)
add_bundle(org.kde.konversation
           PACKAGE konversation
)
add_bundle(org.kde.kcharselect
           PACKAGE kcharselect
)
add_bundle(org.kde.kolourpaint
           PACKAGE kolourpaint
           DEPENDS qimageblitz
)

# GAMES
add_bundle(org.kde.bomber
           PACKAGE bomber
           DEPENDS libkdegames
)
add_bundle(org.kde.kubrick
           PACKAGE kubrick
           DEPENDS libkdegames
)
add_bundle(org.kde.knetwalk
           PACKAGE knetwalk
           DEPENDS libkdegames
)
add_bundle(org.kde.khangman
          PACKAGE khangman
          DEPENDS libkdegames libkeduvocdocument
)
