# coding=utf-8
from __future__ import absolute_import

import logging
import octoprint.plugin
import octoprint.printer
import sys
from . import gvariables
import time


class Server_probingPlugin(octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.SimpleApiPlugin,
                           octoprint.plugin.AssetPlugin,
                           octoprint.plugin.TemplatePlugin):
        delay = False

        def __init__(self):
            self.get_position=False
            self.ian_debug=False
            self.log="/home/pi/.octoprint/logs/probe.log"
#We should move down when probing (The probe/tool starts above the board. We move it first down to make contact, then up till we loose contact.)
            self.down=True
            self.position={}
            self.active=False
            self.parse=gvariables.gvariables()

        
        def on_api_get(self, request):
            import flask
            if "Toggle" in str(request):
                self.active=not self.active
            return flask.jsonify(on=str(self.active))

	##~~ AssetPlugin mixin

        def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
                return dict(
			js=["js/server_probing.js"],
			css=["css/server_probing.css"],
			less=["less/server_probing.less"]
		)

	##~~ Softwareupdate hook

        def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
                return dict(
			server_probing=dict(
				displayName="Server_probing Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="IanCarr-deAvelon",
				repo="server_probing",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/IanCarr-deAvelon/server_probing/archive/{target_version}.zip"
			)
		)



        def handle_gcode_queuing(self, comm_instance, phase, cmd, cmd_type, gcode, subcode=None, tags=None, *args, **kwargs):
            if not self.active:
                return
            if False:
                logger = logging.getLogger("probe")
                logger.setLevel(logging.INFO)
                fh = logging.FileHandler(self.log)
                fh.setLevel(logging.INFO)
                logger.addHandler(fh)
                out="Incoming "
                out+=" GCODE "+str(gcode)+" TAGS "+str(tags)+" CMD "+str(cmd)+" type "+str(cmd_type)
                logger.info(out)
#if this looks like the result of a M114 command, save the Z value
            if not tags is None:
                if "PROBE" in tags:
                    return
#pause on tool change
            if gcode in ["M0"]:
                self._printer.pause_print()
#remove commands which Marlin does not understand
            if gcode in ["G94","G21","G64"]:
                return None,
#            count=0
#            while count <10:
#                if Server_probingPlugin.delay:
#                count+=1
#if a probe command is about to be sent to the machine 
            if not gcode is None:
                if "G31" in gcode:
                    self._printer.pause_print()
                    Server_probingPlugin.delay=True
                    self.down=True
#remove the instruction from the stream
#run to end instruction to stream
#add show position instruction to stream
#add instrution to report the state of the endstops
#M400 execute stream to here, M114 to find where we are and M119 report endstops
#                    return ["M400 ","M114 ","M119 "]
                    self.get_position=True
                    return [("M400"),("M114"),("M119")]
#                    return [("M400 ","",{"PROBE"}),("M114 ","",{"PROBE"}),("M119 ","",{"PROBE"})]
#use the gvariables module to deal with anything Marlin lacks
            parsed=self.parse.parse(cmd)
            if type(parsed) ==  tuple:
               return None,
            return (parsed,cmd_type)
#            return (cmd,)

        def handle_gcode_sent(self, comm_instance, phase, cmd, cmd_type, gcode, subcode=None, tags=None, *args, **kwargs):
            if not self.active:
                return
            return
#Once the report endstops instruction is sent, pause the stream so we can 
#take control of the machine
            if gcode is None:
               return None,
            if "M119" in gcode:
                with self._printer.job_on_hold():
                    self.delay =True 
                    while self.delay:
                        time.sleep(0.25)
            return
            """
                if self._printer.set_job_on_hold(True):
                    try:
                        self.delay=True
                        while self.delay:
                            time.sleep(0.25)
                    finally:
                        self._printer.set_job_on_hold(False)
            """
#octoprint's pause is too slow try hold 
#                self._printer.set_job_on_hold(True, True)
                

        def handle_gcode_received(self, comm_instance,line,*args, **kwargs):
            END_STOP=("M119")
            if not self.active:
                return line
#IAN3
#            return line
            if self.ian_debug:
                out="Incomming "
                if not line is None :
                    out+=" LINE "+line
                    logger.info(out)
#if this looks like the result of a M114 command, save the Z value
#Example
#X:1.00 Y:85.00 Z:30.00 E:0.00 Count X:100 Y:8500 Z:12000 
            if "Count" in line and self.get_position:
                self.get_position=False
                for pos in line[:line.find("Count")].split(): 
                    axes=pos.split(":")
                    self.position[axes[0]]=float(axes[1])
# y_min: open
            if "y_min:" in line:
#don't start till we've paused
                if not self._printer.is_paused():
                    self._printer.commands([("M117 wait"),("M119")], tags={"PROBE"},  force=True)
                    return line
                if self.down:
                    if "open" in line:
                        self.position["Z"]+=-0.1
#Move and at end check the endstops again 
#don't send zero as some floating point value Marlin can't understand
                        if abs(self.position["Z"]) < 0.01:
                            self._printer.commands([("M117 probe "+str(self.position["Z"])),("G00 Z0"),("M119")], tags={"PROBE"},  force=True)
                        else:
                            self._printer.commands([("M117 probe "+str(self.position["Z"])),("G00 Z"+str(self.position["Z"])),("M119")], tags={"PROBE"},  force=True)
                    else:
                       self.down=False
                       self.position["Z"]+=0.01
                       self._printer.commands([("M117 found "+str(self.position["Z"])),("G00 Z"+str(self.position["Z"])),END_STOP], tags={"PROBE"}, force=True)
                else:
                    if "open" in line:
                       self._printer.commands([("M117 done "+str(self.position["Z"])),("G00 Z"+str(self.position["Z"]+1.0))], tags={"PROBE"}, force=True)
#store the probed value in the gvariables #2002 variable
                       self.parse.variables[2002]=self.position["Z"]
                       self.down=True
                       Server_probingPlugin.delay=False
#don't resume till we've paused
#                       while not self._printer.is_paused():
#                           time.sleep(1)
                       self._printer.resume_print()
                    else:
                       self.position["Z"]+=0.01
                       self._printer.commands([("M117 riseing "+str(self.position["Z"])),("G00 Z"+str(self.position["Z"])),END_STOP], tags={"PROBE"}, force=True)
            return line

        __plugin_name__ = "Server_probing"
        __plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3


def __plugin_load__():
    ian_debug=True
    log="/home/pi/.octoprint/logs/probe.log"
    if ian_debug:
        logger = logging.getLogger("probe")
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        if ian_debug:
                    logger.info("Probing loading")


    global __plugin_implementation__
    __plugin_implementation__ = Server_probingPlugin()


    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.handle_gcode_queuing,

        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.handle_gcode_sent,

        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.handle_gcode_received,


        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
        }

