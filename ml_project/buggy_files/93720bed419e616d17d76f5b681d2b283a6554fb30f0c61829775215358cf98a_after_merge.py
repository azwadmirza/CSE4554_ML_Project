	def _createDetachedPanel( self, *args, **kwargs ) :

		panel = _DetachedPanel( self,  *args, **kwargs )
		panel.__removeOnCloseConnection = panel.closedSignal().connect( lambda w : w.parent()._removeDetachedPanel( w ) )

		scriptWindow = self.ancestor( GafferUI.ScriptWindow )
		if scriptWindow :
			panel.setTitle( scriptWindow.getTitle() )
			weakSetTitle = Gaffer.WeakMethod( panel.setTitle )
			panel.__titleChangedConnection = scriptWindow.titleChangedSignal().connect( lambda w, t : weakSetTitle( t ) )

		self.__detachedPanels.append( panel )
		return panel