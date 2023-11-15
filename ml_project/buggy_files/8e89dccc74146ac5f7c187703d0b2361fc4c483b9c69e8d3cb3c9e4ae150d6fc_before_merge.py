	def _removeDetachedPanel( self, panel ) :

		self.__detachedPanels.remove( panel )
		panel.__removeOnCloseConnection = None
		panel._applyVisibility()