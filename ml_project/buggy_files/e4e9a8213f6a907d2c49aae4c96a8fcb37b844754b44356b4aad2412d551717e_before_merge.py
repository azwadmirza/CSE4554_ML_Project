	def _openSerial(self):
		def default(_, port, baudrate, read_timeout):
			if port is None or port == 'AUTO':
				# no known port, try auto detection
				self._changeState(self.STATE_DETECT_SERIAL)
				port = self._detect_port()
				if port is None:
					error_text = "Failed to autodetect serial port, please set it manually."
					self._trigger_error(error_text, "autodetect_port")
					self._log(error_text)
					return None

			# connect to regular serial port
			self._log("Connecting to: %s" % port)

			serial_port_args = {
				"baudrate": baudrateList()[0] if baudrate == 0 else baudrate,
				"timeout": read_timeout,
				"write_timeout": 0,
			}

			if settings().getBoolean(["serial", "exclusive"]):
				serial_port_args["exclusive"] = True

			serial_obj = serial.Serial(**serial_port_args)
			serial_obj.port = str(port)

			use_parity_workaround = settings().get(["serial", "useParityWorkaround"])
			needs_parity_workaround = get_os() == "linux" and os.path.exists("/etc/debian_version") # See #673

			if use_parity_workaround == "always" or (needs_parity_workaround and use_parity_workaround == "detect"):
				serial_obj.parity = serial.PARITY_ODD
				serial_obj.open()
				serial_obj.close()
				serial_obj.parity = serial.PARITY_NONE

			serial_obj.open()

			return BufferedReadlineWrapper(serial_obj)

		serial_factories = self._serial_factory_hooks.items() + [("default", default)]
		for name, factory in serial_factories:
			try:
				serial_obj = factory(self, self._port, self._baudrate, settings().getFloat(["serial", "timeout", "connection"]))
			except:
				exception_string = get_exception_string()
				self._trigger_error("Connection error, see Terminal tab", "connection")

				error_message = "Unexpected error while connecting to serial port: %s %s (hook %s)" % (self._port, exception_string, name)
				self._log(error_message)
				self._logger.exception(error_message)

				if "failed to set custom baud rate" in exception_string.lower():
					self._log("Your installation does not support custom baudrates (e.g. 250000) for connecting to your printer. This is a problem of the pyserial library that OctoPrint depends on. Please update to a pyserial version that supports your baudrate or switch your printer's firmware to a standard baudrate (e.g. 115200). See https://github.com/foosel/OctoPrint/wiki/OctoPrint-support-for-250000-baud-rate-on-Raspbian")

				return False

			if serial_obj is not None:
				# first hook to succeed wins, but any can pass on to the next
				self._changeState(self.STATE_OPEN_SERIAL)
				self._serial = serial_obj
				self._clear_to_send.reset()
				return True

		return False