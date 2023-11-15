	def __setTabDragConstraints( self, qTabBar, event ) :

		# We need to work out some min/max X coordinates (in the tab bars local
		# space) such that when the user drags left/rigth the left/right edges
		# of the tab never leave the TabBar.
		tabRect = qTabBar.tabRect( qTabBar.currentIndex() )
		self.__dragMinX = event.pos().x() - tabRect.x() # cursorToTabLeftEdge
		cursorToTabRightEdge = tabRect.x() + tabRect.width() - event.pos().x()
		self.__dragMaxX = qTabBar.width() - cursorToTabRightEdge