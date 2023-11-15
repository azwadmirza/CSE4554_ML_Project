	def call(self, command, **kwargs):
		"""
		Calls a command

		Args:
		    command (list, tuple or str): command to call
		    kwargs (dict): additional keyword arguments to pass to the sarge ``run`` call (note that ``_async``,
		                   ``stdout`` and ``stderr`` will be overwritten)

		Returns:
		    (tuple) a 3-tuple of return code, full stdout and full stderr output
		"""

		if isinstance(command, (list, tuple)):
			joined_command = " ".join(command)
		else:
			joined_command = command
		self._logger.debug("Calling: {}".format(joined_command))
		self.on_log_call(joined_command)

		# if we are running under windows, make sure there are no unicode strings in the env
		if get_os() == "windows" and "env" in kwargs:
			kwargs["env"] = dict((k, to_bytes(v)) for k, v in kwargs["env"].items())

		kwargs.update(dict(async_=True, stdout=sarge.Capture(), stderr=sarge.Capture()))

		p = sarge.run(command, **kwargs)
		while len(p.commands) == 0:
			# somewhat ugly... we can't use wait_events because
			# the events might not be all set if an exception
			# by sarge is triggered within the async process
			# thread
			time.sleep(0.01)

		# by now we should have a command, let's wait for its
		# process to have been prepared
		p.commands[0].process_ready.wait()

		if not p.commands[0].process:
			# the process might have been set to None in case of any exception
			self._logger.error("Error while trying to run command {}".format(joined_command))
			return None, [], []

		all_stdout = []
		all_stderr = []

		def process_lines(lines, logger):
			if not lines:
				return []
			l = self._preprocess_lines(*map(lambda x: to_unicode(x, errors="replace"), lines))
			logger(*l)
			return list(l)

		def process_stdout(lines):
			return process_lines(lines, self._log_stdout)

		def process_stderr(lines):
			return process_lines(lines, self._log_stderr)

		try:
			while p.returncode is None:
				all_stderr += process_stderr(p.stderr.readlines(timeout=0.5))
				all_stdout += process_stdout(p.stdout.readlines(timeout=0.5))
				p.commands[0].poll()

		finally:
			p.close()

		all_stderr += process_stderr(p.stderr.readlines())
		all_stdout += process_stdout(p.stdout.readlines())

		return p.returncode, all_stdout, all_stderr