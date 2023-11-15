def __showLocalDispatcherWindow( menu ) :
	
	window = _LocalJobsWindow.acquire( Gaffer.LocalDispatcher.defaultJobPool() )
	scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
	scriptWindow.addChildWindow( window )
	window.setVisible( True )