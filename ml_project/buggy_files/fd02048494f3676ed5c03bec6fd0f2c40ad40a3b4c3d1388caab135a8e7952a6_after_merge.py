	def _popupMenuDefinition( self ) :

		menuDefinition = IECore.MenuDefinition()

		if self.getPlug().getInput() is not None :
			menuDefinition.append( "/Edit input...", { "command" : Gaffer.WeakMethod( self.__editInput ) } )
			menuDefinition.append( "/EditInputDivider", { "divider" : True } )
			menuDefinition.append(
				"/Remove input", {
					"command" : Gaffer.WeakMethod( self.__removeInput ),
					"active" : self.getPlug().acceptsInput( None ) and not self.getReadOnly(),
				}
			)
		if hasattr( self.getPlug(), "defaultValue" ) and self.getPlug().direction() == Gaffer.Plug.Direction.In :
			menuDefinition.append(
				"/Default", {
					"command" : IECore.curry( Gaffer.WeakMethod( self.__setValue ), self.getPlug().defaultValue() ),
					"active" : self._editable()
				}
			)

		if Gaffer.NodeAlgo.hasUserDefault( self.getPlug() ) and self.getPlug().direction() == Gaffer.Plug.Direction.In :
			menuDefinition.append(
				"/User Default", {
					"command" : Gaffer.WeakMethod( self.__applyUserDefault ),
					"active" : self._editable()
				}
			)
		
		with self.getContext() :
			currentPreset = Gaffer.NodeAlgo.currentPreset( self.getPlug() )
		
		for presetName in Gaffer.NodeAlgo.presets( self.getPlug() ) :
			menuDefinition.append(
				"/Preset/" + presetName, {
					"command" : IECore.curry( Gaffer.WeakMethod( self.__applyPreset ), presetName ),
					"active" : self._editable(),
					"checkBox" : presetName == currentPreset,
				}
			)
		
		self.popupMenuSignal()( menuDefinition, self )

		return menuDefinition