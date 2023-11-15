def _saveSettings(data):
	logger = logging.getLogger(__name__)

	s = settings()

	# NOTE: Remember to adjust the docs of the data model on the Settings API if anything
	# is changed, added or removed here

	if "folder" in data:
		try:
			if "uploads" in data["folder"]: s.setBaseFolder("uploads", data["folder"]["uploads"])
			if "timelapse" in data["folder"]: s.setBaseFolder("timelapse", data["folder"]["timelapse"])
			if "timelapseTmp" in data["folder"]: s.setBaseFolder("timelapse_tmp", data["folder"]["timelapseTmp"])
			if "logs" in data["folder"]: s.setBaseFolder("logs", data["folder"]["logs"])
			if "watched" in data["folder"]: s.setBaseFolder("watched", data["folder"]["watched"])
		except IOError:
			return make_response("One of the configured folders is invalid", 400)

	if "api" in data:
		if "allowCrossOrigin" in data["api"]: s.setBoolean(["api", "allowCrossOrigin"], data["api"]["allowCrossOrigin"])

	if "appearance" in data:
		if "name" in data["appearance"]: s.set(["appearance", "name"], data["appearance"]["name"])
		if "color" in data["appearance"]: s.set(["appearance", "color"], data["appearance"]["color"])
		if "colorTransparent" in data["appearance"]: s.setBoolean(["appearance", "colorTransparent"], data["appearance"]["colorTransparent"])
		if "colorIcon" in data["appearance"]: s.setBoolean(["appearance", "colorIcon"], data["appearance"]["colorIcon"])
		if "defaultLanguage" in data["appearance"]: s.set(["appearance", "defaultLanguage"], data["appearance"]["defaultLanguage"])
		if "showFahrenheitAlso" in data["appearance"]: s.setBoolean(["appearance", "showFahrenheitAlso"], data["appearance"]["showFahrenheitAlso"])
		if "fuzzyTimes" in data["appearance"]: s.setBoolean(["appearance", "fuzzyTimes"], data["appearance"]["fuzzyTimes"])
		if "closeModalsWithClick" in data["appearance"]: s.setBoolean(["appearance", "closeModalsWithClick"], data["appearance"]["closeModalsWithClick"])

	if "printer" in data:
		if "defaultExtrusionLength" in data["printer"]: s.setInt(["printerParameters", "defaultExtrusionLength"], data["printer"]["defaultExtrusionLength"])

	if "webcam" in data:
		if "webcamEnabled" in data["webcam"]: s.setBoolean(["webcam", "webcamEnabled"], data["webcam"]["webcamEnabled"])
		if "timelapseEnabled" in data["webcam"]: s.setBoolean(["webcam", "timelapseEnabled"], data["webcam"]["timelapseEnabled"])
		if "streamUrl" in data["webcam"]: s.set(["webcam", "stream"], data["webcam"]["streamUrl"])
		if "streamRatio" in data["webcam"] and data["webcam"]["streamRatio"] in ("16:9", "4:3"): s.set(["webcam", "streamRatio"], data["webcam"]["streamRatio"])
		if "streamTimeout" in data["webcam"]: s.setInt(["webcam", "streamTimeout"], data["webcam"]["streamTimeout"])
		if "snapshotUrl" in data["webcam"]: s.set(["webcam", "snapshot"], data["webcam"]["snapshotUrl"])
		if "snapshotTimeout" in data["webcam"]: s.setInt(["webcam", "snapshotTimeout"], data["webcam"]["snapshotTimeout"])
		if "snapshotSslValidation" in data["webcam"]: s.setBoolean(["webcam", "snapshotSslValidation"], data["webcam"]["snapshotSslValidation"])
		if "ffmpegPath" in data["webcam"]: s.set(["webcam", "ffmpeg"], data["webcam"]["ffmpegPath"])
		if "bitrate" in data["webcam"]: s.set(["webcam", "bitrate"], data["webcam"]["bitrate"])
		if "ffmpegThreads" in data["webcam"]: s.setInt(["webcam", "ffmpegThreads"], data["webcam"]["ffmpegThreads"])
		if "ffmpegVideoCodec" in data["webcam"] and data["webcam"]["ffmpegVideoCodec"] in ("mpeg2video", "libx264"): s.set(["webcam", "ffmpegVideoCodec"], data["webcam"]["ffmpegVideoCodec"])
		if "watermark" in data["webcam"]: s.setBoolean(["webcam", "watermark"], data["webcam"]["watermark"])
		if "flipH" in data["webcam"]: s.setBoolean(["webcam", "flipH"], data["webcam"]["flipH"])
		if "flipV" in data["webcam"]: s.setBoolean(["webcam", "flipV"], data["webcam"]["flipV"])
		if "rotate90" in data["webcam"]: s.setBoolean(["webcam", "rotate90"], data["webcam"]["rotate90"])

	if "feature" in data:
		if "temperatureGraph" in data["feature"]: s.setBoolean(["feature", "temperatureGraph"], data["feature"]["temperatureGraph"])
		if "sdSupport" in data["feature"]: s.setBoolean(["feature", "sdSupport"], data["feature"]["sdSupport"])
		if "keyboardControl" in data["feature"]: s.setBoolean(["feature", "keyboardControl"], data["feature"]["keyboardControl"])
		if "pollWatched" in data["feature"]: s.setBoolean(["feature", "pollWatched"], data["feature"]["pollWatched"])
		if "modelSizeDetection" in data["feature"]: s.setBoolean(["feature", "modelSizeDetection"], data["feature"]["modelSizeDetection"])
		if "printStartConfirmation" in data["feature"]: s.setBoolean(["feature", "printStartConfirmation"], data["feature"]["printStartConfirmation"])
		if "printCancelConfirmation" in data["feature"]: s.setBoolean(["feature", "printCancelConfirmation"], data["feature"]["printCancelConfirmation"])
		if "g90InfluencesExtruder" in data["feature"]: s.setBoolean(["feature", "g90InfluencesExtruder"], data["feature"]["g90InfluencesExtruder"])
		if "autoUppercaseBlacklist" in data["feature"] and isinstance(data["feature"]["autoUppercaseBlacklist"], (list, tuple)): s.set(["feature", "autoUppercaseBlacklist"], data["feature"]["autoUppercaseBlacklist"])

	if "gcodeAnalysis" in data:
		if "runAt" in data["gcodeAnalysis"]: s.set(["gcodeAnalysis", "runAt"], data["gcodeAnalysis"]["runAt"])

	if "serial" in data:
		if "autoconnect" in data["serial"]: s.setBoolean(["serial", "autoconnect"], data["serial"]["autoconnect"])
		if "port" in data["serial"]: s.set(["serial", "port"], data["serial"]["port"])
		if "baudrate" in data["serial"]: s.setInt(["serial", "baudrate"], data["serial"]["baudrate"])
		if "exclusive" in data["serial"]: s.setBoolean(["serial", "exclusive"], data["serial"]["exclusive"])
		if "timeoutConnection" in data["serial"]: s.setFloat(["serial", "timeout", "connection"], data["serial"]["timeoutConnection"], min=1.0)
		if "timeoutDetectionFirst" in data["serial"]: s.setFloat(["serial", "timeout", "detectionFirst"], data["serial"]["timeoutDetectionFirst"], min=1.0)
		if "timeoutDetectionConsecutive" in data["serial"]: s.setFloat(["serial", "timeout", "detectionConsecutive"], data["serial"]["timeoutDetectionConsecutive"], min=1.0)
		if "timeoutCommunication" in data["serial"]: s.setFloat(["serial", "timeout", "communication"], data["serial"]["timeoutCommunicationFirst"], min=1.0)
		if "timeoutCommunicationBusy" in data["serial"]: s.setFloat(["serial", "timeout", "communicationBusy"], data["serial"]["timeoutCommunicationBusy"], min=1.0)
		if "timeoutTemperature" in data["serial"]: s.setFloat(["serial", "timeout", "temperature"], data["serial"]["timeoutTemperature"], min=1.0)
		if "timeoutTemperatureTargetSet" in data["serial"]: s.setFloat(["serial", "timeout", "temperatureTargetSet"], data["serial"]["timeoutTemperatureTargetSet"], min=1.0)
		if "timeoutTemperatureAutoreport" in data["serial"]: s.setFloat(["serial", "timeout", "temperatureAutoreport"], data["serial"]["timeoutTemperatureAutoreport"], min=0.0)
		if "timeoutSdStatus" in data["serial"]: s.setFloat(["serial", "timeout", "sdStatus"], data["serial"]["timeoutSdStatus"], min=1.0)
		if "timeoutSdStatusAutoreport" in data["serial"]: s.setFloat(["serial", "timeout", "sdStatusAutoreport"], data["serial"]["timeoutSdStatusAutoreport"], min=0.0)
		if "timeoutBaudrateDetectionPause" in data["serial"]: s.setFloat(["serial", "timeout", "baudrateDetectionPause"], data["serial"]["timeoutBaudrateDetectionPause"], min=0.0)
		if "timeoutPositionLogWait" in data["serial"]: s.setFloat(["serial", "timeout", "positionLogWait"], data["serial"]["timeoutPositionLogWait"], min=1.0)
		if "additionalPorts" in data["serial"] and isinstance(data["serial"]["additionalPorts"], (list, tuple)): s.set(["serial", "additionalPorts"], data["serial"]["additionalPorts"])
		if "additionalBaudrates" in data["serial"] and isinstance(data["serial"]["additionalBaudrates"], (list, tuple)): s.set(["serial", "additionalBaudrates"], data["serial"]["additionalBaudrates"])
		if "blacklistedPorts" in data["serial"] and isinstance(data["serial"]["blacklistedPorts"], (list, tuple)): s.set(["serial", "blacklistedPorts"], data["serial"]["blacklistedPorts"])
		if "blacklistedBaudrates" in data["serial"] and isinstance(data["serial"]["blacklistedBaudrates"], (list, tuple)): s.set(["serial", "blacklistedBaudrates"], data["serial"]["blacklistedBaudrates"])
		if "longRunningCommands" in data["serial"] and isinstance(data["serial"]["longRunningCommands"], (list, tuple)): s.set(["serial", "longRunningCommands"], data["serial"]["longRunningCommands"])
		if "checksumRequiringCommands" in data["serial"] and isinstance(data["serial"]["checksumRequiringCommands"], (list, tuple)): s.set(["serial", "checksumRequiringCommands"], data["serial"]["checksumRequiringCommands"])
		if "blockedCommands" in data["serial"] and isinstance(data["serial"]["blockedCommands"], (list, tuple)): s.set(["serial", "blockedCommands"], data["serial"]["blockedCommands"])
		if "pausingCommands" in data["serial"] and isinstance(data["serial"]["pausingCommands"], (list, tuple)): s.set(["serial", "pausingCommands"], data["serial"]["pausingCommands"])
		if "emergencyCommands" in data["serial"] and isinstance(data["serial"]["emergencyCommands"], (list, tuple)): s.set(["serial", "emergencyCommands"], data["serial"]["emergencyCommands"])
		if "helloCommand" in data["serial"]: s.set(["serial", "helloCommand"], data["serial"]["helloCommand"])
		if "ignoreErrorsFromFirmware" in data["serial"]: s.setBoolean(["serial", "ignoreErrorsFromFirmware"], data["serial"]["ignoreErrorsFromFirmware"])
		if "disconnectOnErrors" in data["serial"]: s.setBoolean(["serial", "disconnectOnErrors"], data["serial"]["disconnectOnErrors"])
		if "triggerOkForM29" in data["serial"]: s.setBoolean(["serial", "triggerOkForM29"], data["serial"]["triggerOkForM29"])
		if "supportResendsWithoutOk" in data["serial"]:
			value = data["serial"]["supportResendsWithoutOk"]
			if value in ("always", "detect", "never"):
				s.set(["serial", "supportResendsWithoutOk"], value)
		if "waitForStart" in data["serial"]: s.setBoolean(["serial", "waitForStartOnConnect"], data["serial"]["waitForStart"])
		if "alwaysSendChecksum" in data["serial"]: s.setBoolean(["serial", "alwaysSendChecksum"], data["serial"]["alwaysSendChecksum"])
		if "neverSendChecksum" in data["serial"]: s.setBoolean(["serial", "neverSendChecksum"], data["serial"]["neverSendChecksum"])
		if "sdRelativePath" in data["serial"]: s.setBoolean(["serial", "sdRelativePath"], data["serial"]["sdRelativePath"])
		if "sdAlwaysAvailable" in data["serial"]: s.setBoolean(["serial", "sdAlwaysAvailable"], data["serial"]["sdAlwaysAvailable"])
		if "swallowOkAfterResend" in data["serial"]: s.setBoolean(["serial", "swallowOkAfterResend"], data["serial"]["swallowOkAfterResend"])
		if "repetierTargetTemp" in data["serial"]: s.setBoolean(["serial", "repetierTargetTemp"], data["serial"]["repetierTargetTemp"])
		if "externalHeatupDetection" in data["serial"]: s.setBoolean(["serial", "externalHeatupDetection"], data["serial"]["externalHeatupDetection"])
		if "ignoreIdenticalResends" in data["serial"]: s.setBoolean(["serial", "ignoreIdenticalResends"], data["serial"]["ignoreIdenticalResends"])
		if "firmwareDetection" in data["serial"]: s.setBoolean(["serial", "firmwareDetection"], data["serial"]["firmwareDetection"])
		if "blockWhileDwelling" in data["serial"]: s.setBoolean(["serial", "blockWhileDwelling"], data["serial"]["blockWhileDwelling"])
		if "useParityWorkaround" in data["serial"]:
			value = data["serial"]["useParityWorkaround"]
			if value in ("always", "detect", "never"):
				s.set(["serial", "useParityWorkaround"], value)
		if "sanityCheckTools" in data["serial"]: s.setBoolean(["serial", "sanityCheckTools"], data["serial"]["sanityCheckTools"])
		if "sendM112OnError" in data["serial"]: s.setBoolean(["serial", "sendM112OnError"], data["serial"]["sendM112OnError"])
		if "disableSdPrintingDetection" in data["serial"]: s.setBoolean(["serial", "disableSdPrintingDetection"], data["serial"]["disableSdPrintingDetection"])
		if "ackMax" in data["serial"]: s.setInt(["serial", "ackMax"], data["serial"]["ackMax"])
		if "logPositionOnPause" in data["serial"]: s.setBoolean(["serial", "logPositionOnPause"], data["serial"]["logPositionOnPause"])
		if "logPositionOnCancel" in data["serial"]: s.setBoolean(["serial", "logPositionOnCancel"], data["serial"]["logPositionOnCancel"])
		if "abortHeatupOnCancel" in data["serial"]: s.setBoolean(["serial", "abortHeatupOnCancel"], data["serial"]["abortHeatupOnCancel"])
		if "maxTimeoutsIdle" in data["serial"]: s.setInt(["serial", "maxCommunicationTimeouts", "idle"], data["serial"]["maxTimeoutsIdle"])
		if "maxTimeoutsPrinting" in data["serial"]: s.setInt(["serial", "maxCommunicationTimeouts", "printing"], data["serial"]["maxTimeoutsPrinting"])
		if "maxTimeoutsLong" in data["serial"]: s.setInt(["serial", "maxCommunicationTimeouts", "long"], data["serial"]["maxTimeoutsLong"])
		if "capAutoreportTemp" in data["serial"]: s.setBoolean(["serial", "capabilities", "autoreport_temp"], data["serial"]["capAutoreportTemp"])
		if "capAutoreportSdStatus" in data["serial"]: s.setBoolean(["serial", "capabilities", "autoreport_sdstatus"], data["serial"]["capAutoreportSdStatus"])
		if "capBusyProtocol" in data["serial"]: s.setBoolean(["serial", "capabilities", "busy_protocol"], data["serial"]["capBusyProtocol"])
		if "capEmergencyParser" in data["serial"]: s.setBoolean(["serial", "capabilities", "emergency_parser"], data["serial"]["capEmergencyParser"])

		oldLog = s.getBoolean(["serial", "log"])
		if "log" in data["serial"]: s.setBoolean(["serial", "log"], data["serial"]["log"])
		if oldLog and not s.getBoolean(["serial", "log"]):
			# disable debug logging to serial.log
			logging.getLogger("SERIAL").debug("Disabling serial logging")
			logging.getLogger("SERIAL").setLevel(logging.CRITICAL)
		elif not oldLog and s.getBoolean(["serial", "log"]):
			# enable debug logging to serial.log
			logging.getLogger("SERIAL").setLevel(logging.DEBUG)
			logging.getLogger("SERIAL").debug("Enabling serial logging")

	if "temperature" in data:
		if "profiles" in data["temperature"]:
			result = []
			for profile in data["temperature"]["profiles"]:
				try:
					profile["bed"] = int(profile["bed"])
					profile["extruder"] = int(profile["extruder"])
				except ValueError:
					pass
				result.append(profile)
			s.set(["temperature", "profiles"], result)
		if "cutoff" in data["temperature"]:
			try:
				cutoff = int(data["temperature"]["cutoff"])
				if cutoff > 1:
					s.setInt(["temperature", "cutoff"], cutoff)
			except ValueError:
				pass
		if "sendAutomatically" in data["temperature"]: s.setBoolean(["temperature", "sendAutomatically"], data["temperature"]["sendAutomatically"])
		if "sendAutomaticallyAfter" in data["temperature"]: s.setInt(["temperature", "sendAutomaticallyAfter"], data["temperature"]["sendAutomaticallyAfter"], min=0, max=30)

	if "terminalFilters" in data:
		s.set(["terminalFilters"], data["terminalFilters"])

	if "system" in data:
		if "actions" in data["system"]: s.set(["system", "actions"], data["system"]["actions"])
		if "events" in data["system"]: s.set(["system", "events"], data["system"]["events"])

	if "scripts" in data:
		if "gcode" in data["scripts"] and isinstance(data["scripts"]["gcode"], dict):
			for name, script in data["scripts"]["gcode"].items():
				if name == "snippets":
					continue
				s.saveScript("gcode", name, script.replace("\r\n", "\n").replace("\r", "\n"))

	if "server" in data:
		if "commands" in data["server"]:
			if "systemShutdownCommand" in data["server"]["commands"]: s.set(["server", "commands", "systemShutdownCommand"], data["server"]["commands"]["systemShutdownCommand"])
			if "systemRestartCommand" in data["server"]["commands"]: s.set(["server", "commands", "systemRestartCommand"], data["server"]["commands"]["systemRestartCommand"])
			if "serverRestartCommand" in data["server"]["commands"]: s.set(["server", "commands", "serverRestartCommand"], data["server"]["commands"]["serverRestartCommand"])
		if "diskspace" in data["server"]:
			if "warning" in data["server"]["diskspace"]: s.setInt(["server", "diskspace", "warning"], data["server"]["diskspace"]["warning"])
			if "critical" in data["server"]["diskspace"]: s.setInt(["server", "diskspace", "critical"], data["server"]["diskspace"]["critical"])
		if "onlineCheck" in data["server"]:
			if "enabled" in data["server"]["onlineCheck"]: s.setBoolean(["server", "onlineCheck", "enabled"], data["server"]["onlineCheck"]["enabled"])
			if "interval" in data["server"]["onlineCheck"]:
				try:
					interval = int(data["server"]["onlineCheck"]["interval"])
					s.setInt(["server", "onlineCheck", "interval"], interval*60)
				except ValueError:
					pass
			if "host" in data["server"]["onlineCheck"]: s.set(["server", "onlineCheck", "host"], data["server"]["onlineCheck"]["host"])
			if "port" in data["server"]["onlineCheck"]: s.setInt(["server", "onlineCheck", "port"], data["server"]["onlineCheck"]["port"])
			if "name" in data["server"]["onlineCheck"]: s.set(["server", "onlineCheck", "name"], data["server"]["onlineCheck"]["name"])
		if "pluginBlacklist" in data["server"]:
			if "enabled" in data["server"]["pluginBlacklist"]: s.setBoolean(["server", "pluginBlacklist", "enabled"], data["server"]["pluginBlacklist"]["enabled"])
			if "url" in data["server"]["pluginBlacklist"]: s.set(["server", "pluginBlacklist", "url"], data["server"]["pluginBlacklist"]["url"])
			if "ttl" in data["server"]["pluginBlacklist"]:
				try:
					ttl = int(data["server"]["pluginBlacklist"]["ttl"])
					s.setInt(["server", "pluginBlacklist", "ttl"], ttl * 60)
				except ValueError:
					pass
		if "allowFraming" in data["server"]:
			s.setBoolean(["server", "allowFraming"], data["server"]["allowFraming"])

	if "plugins" in data:
		for plugin in octoprint.plugin.plugin_manager().get_implementations(octoprint.plugin.SettingsPlugin):
			plugin_id = plugin._identifier
			if plugin_id in data["plugins"]:
				try:
					plugin.on_settings_save(data["plugins"][plugin_id])
				except TypeError:
					logger.warning("Could not save settings for plugin {name} ({version}) since it called super(...)".format(name=plugin._plugin_name, version=plugin._plugin_version))
					logger.warning("in a way which has issues due to OctoPrint's dynamic reloading after plugin operations.")
					logger.warning("Please contact the plugin's author and ask to update the plugin to use a direct call like")
					logger.warning("octoprint.plugin.SettingsPlugin.on_settings_save(self, data) instead.")
				except Exception:
					logger.exception("Could not save settings for plugin {name} ({version})".format(version=plugin._plugin_version,
					                                                                                name=plugin._plugin_name),
					                 extra=dict(plugin=plugin._identifier))

	s.save(trigger_event=True)