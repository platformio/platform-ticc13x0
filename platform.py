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

from platform import system

from platformio.managers.platform import PlatformBase
from platformio.util import get_systype


class Ticc13x0Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if not variables.get("board"):
            return PlatformBase.configure_default_packages(
                self, variables, targets)
        board = self.board_config(variables.get("board"))
        upload_protocol = variables.get("upload_protocol",
                                        board.get("upload.protocol", ""))
        disabled_pkgs = []
        upload_tool = "tool-openocd"
        if upload_protocol == "jlink":
            upload_tool = "tool-jlink"
        elif upload_protocol == "dslite":
            upload_tool = "tool-dslite"

        if upload_tool:
            for name, opts in self.packages.items():
                if "type" not in opts or opts['type'] != "uploader":
                    continue
                if name != upload_tool:
                    disabled_pkgs.append(name)

        if "arduino" in variables.get("pioframework", []):
            framework_package = "framework-energia-%s" % (
                "ticc13x0" if board.get("build.mcu", "").startswith("cc13") else "ticc13x0")

            self.frameworks["arduino"]["package"] = framework_package
            if framework_package in self.packages:
                self.packages[framework_package]["optional"] = False

        for name in disabled_pkgs:
            del self.packages[name]
        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug['tools'] = {}

        # J-Link, XDS110
        tools = ("jlink", "xds110")
        for link in tools:
            if link not in upload_protocols or link in debug['tools']:
                continue

            if link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug['tools'][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "JTAG",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if system() == "Windows" else
                                       "JLinkGDBServer")
                    },
                    "onboard": link in debug.get("onboard_tools", [])
                }

            else:
                openocd_chipname = debug.get("openocd_chipname")
                assert openocd_chipname
                openocd_cmds = ["set CHIPNAME %s" % openocd_chipname]
                server_args = [
                    "-s", "$PACKAGE_DIR/scripts",
                    "-f", "interface/%s.cfg" % (link),
                    "-c", "; ".join(openocd_cmds),
                    "-f", "target/%s.cfg" % debug.get("openocd_target")
                ]
                debug['tools'][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    },
                    "onboard": link in debug.get("onboard_tools", [])
                }

        board.manifest['debug'] = debug
        return board
