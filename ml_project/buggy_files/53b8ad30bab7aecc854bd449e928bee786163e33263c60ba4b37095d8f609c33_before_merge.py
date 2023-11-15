	def generate_1_1(self) :
		"""Generate the property object, 1.1 version"""
				
		#########################################################################		
		# See if the target is _not_ a literal
		irirefs      = ("resource", "href", "src")
		noiri        = ("content", "datatype", "rel", "rev")
		notypediri   = ("content", "datatype", "rel", "rev", "about", "about_pruned")
		if has_one_of_attributes(self.node, irirefs) and not has_one_of_attributes(self.node, noiri) :
			# @href/@resource/@src takes the lead here...
			object = self.state.getResource(irirefs)
		elif self.node.hasAttribute("typeof") and not has_one_of_attributes(self.node, notypediri) and self.typed_resource != None :
				# a @typeof creates a special branch in case the typed resource was set during parsing
				object = self.typed_resource
		else :
			# We have to generate a literal
			
			# Get, if exists, the value of @datatype
			datatype = ''
			dtset    = False
			if self.node.hasAttribute("datatype") :
				dtset = True
				dt = self.node.getAttribute("datatype")
				if dt != "" :
					datatype = self.state.getURI("datatype")
		
			# Supress lange is set in case some elements explicitly want to supress the effect of language
			# There were discussions, for example, that the <time> element should do so. Although,
			# after all, this was reversed, the functionality is kept in the code in case another
			# element might need it...
			if self.state.lang != None and self.state.supress_lang == False :
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
					object = self._create_Literal(self._get_literal(self.node), lang=lang)
	
		if object != None :
			for prop in self.state.getURI("property") :
				if not isinstance(prop, BNode) :
					if self.node.hasAttribute("inlist") :
						self.state.add_to_list_mapping(prop, object)
					else :			
						self.graph.add( (self.subject, prop, object) )
				else :
					self.state.options.add_warning(err_no_blank_node % "property", warning_type=IncorrectBlankNodeUsage, node=self.node.nodeName)