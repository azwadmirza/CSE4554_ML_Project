def __showLocalDispatcherWindow( menu ) :
	
	window = _LocalJobsWindow.acquire( Gaffer.LocalDispatcher.defaultJobPool() )
	window.setVisible( True )