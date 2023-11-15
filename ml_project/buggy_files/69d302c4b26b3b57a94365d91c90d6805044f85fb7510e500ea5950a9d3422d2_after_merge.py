	def start_timelapse(self, gcode_file):
		self._logger.debug("Starting timelapse for %s" % gcode_file)

		self._image_number = 0
		self._capture_errors = 0
		self._capture_success = 0
		self._in_timelapse = True
		self._gcode_file = os.path.basename(gcode_file)
		self._file_prefix = "{}_{}".format(os.path.splitext(self._gcode_file)[0], time.strftime("%Y%m%d%H%M%S"))