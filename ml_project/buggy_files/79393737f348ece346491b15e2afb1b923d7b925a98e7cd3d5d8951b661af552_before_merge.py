	def importScope(line, blacklist):
		failedImports = []
		alreadyExists = []
		successImports = []
		if len(line.split(',')) > 1:
			ip = line.split(',')[0]
			tags = line.split(',')[1:]
		else:
			ip = line

		if '/' not in ip:
			ip = ip + '/32'
		try:
			isValid = ipaddress.ip_network(ip, False) # False will mask out hostbits for us, ip_network for eventual ipv6 compat
		except ValueError as e:
			failedImports.append(line) # if we hit this ValueError it means that the input couldn't be a CIDR range
			return failedImports, alreadyExists, successImports
		item = ScopeItem.query.filter_by(target=isValid.with_prefixlen).first() # We only want scope items with masked out host bits
		if item:
			# Add in look for tags and append as necessary
			if tags:
				ScopeItem.addTags(item, tags)
			alreadyExists.append(isValid.with_prefixlen)
			return failedImports, alreadyExists, successImports
		else:
			newTarget = ScopeItem(target=isValid.with_prefixlen, blacklist=blacklist)
			db.session.add(newTarget)
			if tags:
				ScopeItem.addTags(newTarget, tags)
			successImports.append(isValid.with_prefixlen)

		return failedImports, alreadyExists, successImports