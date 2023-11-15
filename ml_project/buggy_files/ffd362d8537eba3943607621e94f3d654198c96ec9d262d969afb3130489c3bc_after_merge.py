	def __init__( self, plug, **kw ) :
			
		GafferUI.CompoundNumericPlugValueWidget.__init__( self, plug, **kw )

		self.__swatch = GafferUI.ColorSwatch()
		## \todo How do set maximum height with a public API?
		self.__swatch._qtWidget().setMaximumHeight( 20 )
		
		self._row().append( self.__swatch, expand=True )
						
		self.__buttonPressConnection = self.__swatch.buttonPressSignal().connect( Gaffer.WeakMethod( self.__buttonPress ) )
		
		self.__colorChooserDialogue = None
		self.__blinkBehaviour = None
		
		self._updateFromPlug()