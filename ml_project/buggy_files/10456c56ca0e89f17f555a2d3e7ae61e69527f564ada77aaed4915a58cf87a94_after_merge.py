	def __setTabDragConstraints( self, qTabBar, event ) :

		# We need to work out some min/max X coordinates (in the tab bars local
		# space) such that when the user drags left/right the left/right edges
		# of the tab never leave the TabBar.
		barRect = qTabBar.rect()
		tabRect = qTabBar.tabRect( qTabBar.tabAt( event.pos() ) )
		mouseX = event.pos().x()

		self.__dragMinX = mouseX - tabRect.x() # cursorToTabLeftEdge

		tabRightEdge = tabRect.x() + tabRect.width()
		if tabRightEdge > barRect.width() :
			# Already as far right as it can go
			self.__dragMaxX = mouseX
		else :
			cursorToTabRightEdge = tabRightEdge - mouseX
			self.__dragMaxX = barRect.width() - cursorToTabRightEdge