	def __init__( self, targetWidgets, blinks = 2 ) :
	
		self.__targetWidgets = [ weakref.ref( w ) for w in targetWidgets ]
		self.__initialStates = [ w.getHighlighted() for w in targetWidgets ]
		
		self.__blinks = blinks
		self.__toggleCount = 0
		self.__timer = QtCore.QTimer()
		self.__timer.timeout.connect( self.__blink )