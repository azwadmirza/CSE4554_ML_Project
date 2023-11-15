	def zeroconf_register(self, reg_type, name=None, port=None, txt_record=None):
		"""
		Registers a new service with Zeroconf/Bonjour/Avahi.

		:param reg_type: type of service to register, e.g. "_gntp._tcp"
		:param name: displayable name of the service, if not given defaults to the OctoPrint instance name
		:param port: port to register for the service, if not given defaults to OctoPrint's (public) port
		:param txt_record: optional txt record to attach to the service, dictionary of key-value-pairs
		"""

		if not pybonjour:
			return

		if not name:
			name = self.get_instance_name()
		if not port:
			port = self.port

		params = dict(
			name=name,
			regtype=reg_type,
			port=port
		)
		if txt_record:
			params["txtRecord"] = pybonjour.TXTRecord(txt_record)

		key = (reg_type, port)

		counter = 0
		while True:
			try:
				self._sd_refs[key] = pybonjour.DNSServiceRegister(**params)
				self._logger.info(u"Registered '{name}' for {regtype}".format(**params))
				return True
			except pybonjour.BonjourError as be:
				if be.errorCode == pybonjour.kDNSServiceErr_NameConflict:
					# Name already registered by different service, let's try a counter postfix. See #2852
					counter += 1
					params["name"] = u"{} ({})".format(name, counter)
				else:
					raise