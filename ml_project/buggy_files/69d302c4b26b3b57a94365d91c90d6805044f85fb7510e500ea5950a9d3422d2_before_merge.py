	def start_timelapse(self, gcodeFile):
		self._logger.debug("Starting timelapse for %s" % gcodeFile)

		self._image_number = 0
		self._capture_errors = 0
		self._capture_success = 0
		self._in_timelapse = True
		self._gcode_file = os.path.basename(gcodeFile)
		self._file_prefix = "{}_{}".format(os.path.splitext(self._gcode_file)[0], time.strftime("%Y%m%d%H%M%S"))