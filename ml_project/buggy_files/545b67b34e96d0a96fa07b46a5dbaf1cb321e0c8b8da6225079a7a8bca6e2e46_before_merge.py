	def _getText(self, withFields, formatConfig=None):
		fields = []
		if self.isCollapsed:
			return fields

		if withFields:
			# Get the initial control fields.
			controlStack = []
			rootObj = self.obj
			obj = self._startObj
			ti = self._start
			cannotBeStart = False
			while obj and obj != rootObj:
				field = self._getControlFieldForObject(obj)
				if field:
					if ti._startOffset == 0:
						if not cannotBeStart:
							field["_startOfNode"] = True
					else:
						# We're not at the start of this object, which also means we're not at the start of any ancestors.
						cannotBeStart = True
					fields.insert(0, textInfos.FieldCommand("controlStart", field))
				controlStack.insert(0, field)
				ti = self._getEmbedding(obj)
				obj = ti.obj
		else:
			controlStack = None

		# Get the fields for start.
		fields += list(self._iterRecursiveText(self._start, controlStack, formatConfig))
		if not fields:
			# We're not getting anything, so the object must be dead.
			# (We already handled collapsed above.)
			return fields
		obj = self._startObj
		while fields[-1] is not None:
			# The end hasn't yet been reached, which means it isn't a descendant of obj.
			# Therefore, continue from where obj was embedded.
			if withFields:
				try:
					field = controlStack.pop()
				except IndexError:
					# We're trying to walk up past our root. This can happen if a descendant
					# object within the range died, in which case _iterRecursiveText will
					# never reach our end object and thus won't yield None. This means this
					# range is invalid, so just return nothing.
					log.debugWarning("Tried to walk up past the root. Objects probably dead.")
					return []
				if field:
					# This object had a control field.
					field["_endOfNode"] = True
					fields.append(textInfos.FieldCommand("controlEnd", None))
			ti = self._getEmbedding(obj)
			obj = ti.obj
			if ti.move(textInfos.UNIT_OFFSET, 1) == 0:
				# There's no more text in this object.
				continue
			ti.setEndPoint(self._makeRawTextInfo(obj, textInfos.POSITION_ALL), "endToEnd")
			fields.extend(self._iterRecursiveText(ti, controlStack, formatConfig))
		del fields[-1]

		if withFields:
			# Determine whether the range covers the end of any ancestors of endObj.
			obj = self._endObj
			ti = self._end
			while obj and obj != rootObj:
				field = controlStack.pop()
				if field:
					fields.append(textInfos.FieldCommand("controlEnd", None))
				if ti.compareEndPoints(self._makeRawTextInfo(obj, textInfos.POSITION_ALL), "endToEnd") == 0:
					if field:
						field["_endOfNode"] = True
				else:
					# We're not at the end of this object, which also means we're not at the end of any ancestors.
					break
				ti = self._getEmbedding(obj)
				obj = ti.obj

		return fields