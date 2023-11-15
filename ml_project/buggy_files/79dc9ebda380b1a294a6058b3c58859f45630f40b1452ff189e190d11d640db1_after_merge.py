	def __show( self ) :
		
		# we rebuild each menu every time it's shown, to support the use of callable items to provide
		# dynamic submenus and item states.
		self.__build( self._qtWidget(), self.__definition )
		
		if self.__searchable :
			# Searchable menus need to initialize a search structure so they can be searched without
			# expanding each submenu. The definition is fully expanded, so dynamic submenus that
			# exist will be expanded and searched.
			self.__searchStructure = {}
			self.__initSearch( self.__definition )
			
			# Searchable menus require an extra submenu to display the search results. 
			searchWidget = QtGui.QWidgetAction( self._qtWidget() )
			searchWidget.setObjectName( "GafferUI.Menu.__searchWidget" )
			self.__searchMenu = _Menu( self._qtWidget(), "" )
			self.__searchMenu.aboutToShow.connect( Gaffer.WeakMethod( self.__searchMenuShow ) )
			self.__searchLine = QtGui.QLineEdit()
			self.__searchLine.textEdited.connect( Gaffer.WeakMethod( self.__updateSearchMenu ) )
			self.__searchLine.returnPressed.connect( Gaffer.WeakMethod( self.__searchReturnPressed ) )
			self.__searchLine.setObjectName( "search" )
			if hasattr( self.__searchLine, "setPlaceholderText" ) :
				# setPlaceHolderText appeared in qt 4.7, nuke (6.3 at time of writing) is stuck on 4.6.
				self.__searchLine.setPlaceholderText( "Search..." )
			if self.__lastAction :
				self.__searchLine.setText( self.__lastAction.text() )
				self.__searchMenu.setDefaultAction( self.__lastAction )
			
			self.__searchLine.selectAll()
			searchWidget.setDefaultWidget( self.__searchLine )
			
			firstAction = self._qtWidget().actions()[0] if len( self._qtWidget().actions() ) else None
			self._qtWidget().insertAction( firstAction, searchWidget )
			self._qtWidget().insertSeparator( firstAction )
			self._qtWidget().setActiveAction( searchWidget )
			self.__searchLine.setFocus()