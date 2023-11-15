	def __buttonPress( self, widget, event ) :
		
		if not self._editable() :
		
			if self.__blinkBehaviour is not None :
				self.__blinkBehaviour.stop()
			widgets = [ w for w in self._row()[:len( self.getPlug() )] if not w._editable() ]
			self.__blinkBehaviour = _BlinkBehaviour( widgets )
			self.__blinkBehaviour.start()
			
			return False
				
		# we only store a weak reference to the dialogue, because we want to allow it
		# to manage its own lifetime. this allows it to exist after we've died, which
		# can be useful for the user - they can bring up a node editor to get access to
		# the color chooser, and then close the node editor but keep the floating color
		# chooser. the only reason we keep a reference to the dialogue at all is so that
		# we can avoid opening two at the same time.
		if self.__colorChooserDialogue is None or self.__colorChooserDialogue() is None :
			self.__colorChooserDialogue = weakref.ref(
				_ColorPlugValueDialogue(
					self.getPlug(),
					self.ancestor( GafferUI.Window )
				)
			)

		self.__colorChooserDialogue().setVisible( True )
				
		return True