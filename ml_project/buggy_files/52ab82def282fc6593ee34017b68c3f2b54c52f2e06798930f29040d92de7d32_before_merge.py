def html5_extra_attributes(node, state) :
	"""
	@param node: the current node that could be modified
	@param state: current state
	@type state: L{Execution context<pyRdfa.state.ExecutionContext>}
	"""
	def _get_literal(Pnode):
		"""
		Get (recursively) the full text from a DOM Node.
	
		@param Pnode: DOM Node
		@return: string
		"""
		rc = ""
		for node in Pnode.childNodes:
			if node.nodeType == node.TEXT_NODE:
				rc = rc + node.data
			elif node.nodeType == node.ELEMENT_NODE :
				rc = rc + self._get_literal(node)
		if state.options.space_preserve :
			return rc
		else :
			return re.sub(r'(\r| |\n|\t)+'," ",rc).strip()
		#return re.sub(r'(\r| |\n|\t)+',"",rc).strip()
	# end _getLiteral

	def _set_time(value) :
		if not node.hasAttribute("datatype") :			
			# Check the datatype:
			dt = _format_test(value)
			if dt != plain :
				node.setAttribute("datatype",dt)
		# Finally, set the value itself
		node.setAttribute("content",value)
	# end _set_time

	if not node.hasAttribute("content") :
		# @content has top priority over the others...
		if node.hasAttribute("datetime") :
			_set_time( node.getAttribute("datetime") )
		elif node.hasAttribute("dateTime") :
			_set_time( node.getAttribute("dateTime") )
		elif node.tagName == "time" :
			# Note that a possible @datetime value has already been taken care of
			_set_time( _get_literal(node) )