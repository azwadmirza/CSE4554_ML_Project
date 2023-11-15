	def _render(self):
		"""Rendering runnable."""

		ffmpeg = settings().get(["webcam", "ffmpeg"])
		bitrate = settings().get(["webcam", "bitrate"])
		if ffmpeg is None or bitrate is None:
			self._logger.warning("Cannot create movie, path to ffmpeg or desired bitrate is unset")
			return

		if self._videocodec == 'mpeg2video':
			extension = "mpg"
		else:
			extension = "mp4"

		input = os.path.join(self._capture_dir,
		                     self._capture_format.format(prefix=self._prefix,
		                                                 postfix=self._postfix if self._postfix is not None else ""))
		output = os.path.join(self._output_dir,
		                      self._output_format.format(prefix=self._prefix,
		                                                 postfix=self._postfix if self._postfix is not None else "",
		                                                 extension=extension))

		for i in range(4):
			if os.path.exists(input % i):
				break
		else:
			self._logger.warning("Cannot create a movie, no frames captured")
			self._notify_callback("fail", output, returncode=0, stdout="", stderr="", reason="no_frames")
			return

		hflip = settings().getBoolean(["webcam", "flipH"])
		vflip = settings().getBoolean(["webcam", "flipV"])
		rotate = settings().getBoolean(["webcam", "rotate90"])

		watermark = None
		if settings().getBoolean(["webcam", "watermark"]):
			watermark = os.path.join(os.path.dirname(__file__), "static", "img", "watermark.png")
			if sys.platform == "win32":
				# Because ffmpeg hiccups on windows' drive letters and backslashes we have to give the watermark
				# path a special treatment. Yeah, I couldn't believe it either...
				watermark = watermark.replace("\\", "/").replace(":", "\\\\:")

		# prepare ffmpeg command
		command_str = self._create_ffmpeg_command_string(ffmpeg, self._fps, bitrate, self._threads, input, output,
		                                                 self._videocodec, hflip=hflip, vflip=vflip, rotate=rotate,
		                                                 watermark=watermark)
		self._logger.debug("Executing command: {}".format(command_str))

		with self.render_job_lock:
			try:
				self._notify_callback("start", output)

				self._logger.debug("Parsing ffmpeg output")

				c = CommandlineCaller()
				c.on_log_stderr = self._process_ffmpeg_output
				returncode, stdout_text, stderr_text = c.call(command_str, delimiter=b'\r', buffer_size=512)

				self._logger.debug("Done with parsing")

				if returncode == 0:
					self._notify_callback("success", output)
				else:
					self._logger.warning("Could not render movie, got return code %r: %s" % (returncode, stderr_text))
					self._notify_callback("fail", output, returncode=returncode, stdout=stdout_text, stderr=stderr_text, reason="returncode")
			except Exception:
				self._logger.exception("Could not render movie due to unknown error")
				self._notify_callback("fail", output, reason="unknown")
			finally:
				self._notify_callback("always", output)