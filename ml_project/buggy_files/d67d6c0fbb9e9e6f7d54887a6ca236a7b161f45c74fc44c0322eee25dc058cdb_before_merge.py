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