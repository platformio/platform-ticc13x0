# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Energia

Energia Wiring-based framework enables pretty much anyone to start easily
creating microcontroller-based projects and applications. Its easy-to-use
libraries and functions provide developers of all experience levels to start
blinking LEDs, buzzing buzzers and sensing sensors more quickly than ever
before.

http://energia.nu/reference/
"""

from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-energiaticc13x0")
FRAMEWORK_VERSION = platform.get_package_version("framework-energiaticc13x0")
assert isdir(FRAMEWORK_DIR)


env.Append(
    CPPDEFINES=[
        ("ARDUINO", 10805),
        ("ENERGIA", int(FRAMEWORK_VERSION.split(".")[1])),
        ("printf", "iprintf"),
        ("DEVICE_FAMILY", "cc13x0"),
        ("xdc_target_types__", "gnu/targets/arm/std.h"),
        ("xdc_target_name__", "M3"),
        ("xdc_cfg__xheader__", "configPkg/package/cfg/energia_pm3g.h"),
        ("xdc__nolocalstring", "1"),
        ("CORE_VERSION", "491")
    ],

    CCFLAGS=[
        "-mfloat-abi=soft",
        "-mabi=aapcs"
    ],

    LINKFLAGS=[
        "-Wl,-u,main",
        "-Wl,--check-sections",
        "-Wl,--gc-sections",
        join(FRAMEWORK_DIR, "system", "source", "ti", "devices", "cc13x0", "driverlib", "bin", "gcc", "driverlib.lib")
    ],

    LIBS=[],

    CPPPATH=[
        join(FRAMEWORK_DIR, "system", "energia"),
        join(FRAMEWORK_DIR, "system", "source"),
        join(FRAMEWORK_DIR, "system", "source", "ti", "devices", "cc13x0"),
        join(FRAMEWORK_DIR, "system", "source", "ti", "devices", "cc13x0", "inc"),
        join(FRAMEWORK_DIR, "system", "source", "ti", "devices", "cc13x0", "driverlib"),
        join(FRAMEWORK_DIR, "system", "kernel", "tirtos", "packages", "ti", "sysbios", "posix"),
        join(FRAMEWORK_DIR, "system", "kernel", "tirtos", "packages"),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core")),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"), "ti", "runtime", "wiring"),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"), "ti", "runtime", "wiring", "cc13xx"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant")),
        join(FRAMEWORK_DIR, "system", "source", "ti", "devices", "cc13x0", "driverlib"),
    ],


    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ]
)

if not env.BoardConfig().get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=env.BoardConfig().get("build.arduino.ldscript", ""))

#
# Target: Build Core Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkEnergia"),
    join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))
))

env.Append(LIBS=libs)
