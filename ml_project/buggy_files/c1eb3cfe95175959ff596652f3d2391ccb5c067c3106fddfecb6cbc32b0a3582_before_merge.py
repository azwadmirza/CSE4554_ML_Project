	def generate_1_0(self) :
		"""Generate the property object, 1.0 version"""
				
		#########################################################################		
		# We have to generate a literal indeed.
		# Get, if exists, the value of @datatype
		datatype = ''
		dtset    = False
		if self.node.hasAttribute("datatype") :
			dtset = True
			dt = self.node.getAttribute("datatype")
			if dt != "" :
				datatype = self.state.getURI("datatype")
	
		if self.state.lang != None :
			lang = self.state.lang
		else :
			lang = ''

		# The simple case: separate @content attribute
		if self.node.hasAttribute("content") :
			val = self.node.getAttribute("content")
			# Handling the automatic uri conversion case
			if dtset == False :
				object = Literal(val, lang=lang)
			else :
				object = self._create_Literal(val, datatype=datatype, lang=lang)
			# The value of datatype has been set, and the keyword paramaters take care of the rest
		else :
			# see if there *is* a datatype (even if it is empty!)
			if dtset :
				# yep. The Literal content is the pure text part of the current element:
				# We have to check whether the specified datatype is, in fact, an
				# explicit XML Literal
				if datatype == XMLLiteral :
					litval = self._get_XML_literal(self.node)
					object = Literal(litval,datatype=XMLLiteral)
				elif datatype == HTMLLiteral :
					# I am not sure why this hack is necessary, but otherwise an encoding error occurs
					# In Python3 all this should become moot, due to the unicode everywhere approach...
					if sys.version_info[0] >= 3 :
						object = Literal(self._get_HTML_literal(self.node), datatype=HTMLLiteral)
					else :
						litval = self._get_HTML_literal(self.node)
						o = Literal(litval, datatype=XMLLiteral)	
						object = Literal(o, datatype=HTMLLiteral)					
				else :
					object = self._create_Literal(self._get_literal(self.node), datatype=datatype, lang=lang)
			else :
				# no controlling @datatype. We have to see if there is markup in the contained
				# element
				if True in [ n.nodeType == self.node.ELEMENT_NODE for n in self.node.childNodes ] :
					# yep, and XML Literal should be generated
					object = self._create_Literal(self._get_XML_literal(self.node), datatype=XMLLiteral)
				else :
					# At this point, there might be entities in the string that are returned as real characters by the dom
					# implementation. That should be turned back
					object = self._create_Literal(self._get_literal(self.node), lang=lang)
	
		for prop in self.state.getURI("property") :
			if not isinstance(prop,BNode) :
				self.graph.add( (self.subject,prop,object) )
			else :
				self.state.options.add_warning(err_no_blank_node % "property", warning_type=IncorrectBlankNodeUsage, node=self.node.nodeName)