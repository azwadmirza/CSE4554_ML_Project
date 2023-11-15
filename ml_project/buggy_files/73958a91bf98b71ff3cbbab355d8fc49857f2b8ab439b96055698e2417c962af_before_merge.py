	def __init__( self, plug, parentWindow ) :
	
		GafferUI.ColorChooserDialogue.__init__( 
			self,
			title = plug.relativeName( plug.ancestor( Gaffer.ScriptNode.staticTypeId() ) ),
			color = plug.getValue()
		)

		self.__plug = plug

		node = plug.node()
		self.__nodeParentChangedConnection = node.parentChangedSignal().connect( Gaffer.WeakMethod( self.__destroy ) )
		self.__plugSetConnection = plug.node().plugSetSignal().connect( Gaffer.WeakMethod( self.__plugSet ) )
		
		self.__closedConnection = self.closedSignal().connect( Gaffer.WeakMethod( self.__destroy ) )
		self.__colorChangedConnection = self.colorChooser().colorChangedSignal().connect( Gaffer.WeakMethod( self.__colorChanged ) )
		self.__confirmClickedConnection = self.confirmButton.clickedSignal().connect( Gaffer.WeakMethod( self.__buttonClicked ) )
		self.__cancelClickedConnection = self.cancelButton.clickedSignal().connect( Gaffer.WeakMethod( self.__buttonClicked ) )

		parentWindow.addChildWindow( self )