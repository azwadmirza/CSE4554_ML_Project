	def acquire( jobPool ) :
		
		assert( isinstance( jobPool, Gaffer.LocalDispatcher.JobPool ) )
		
		window = getattr( jobPool, "_window", None )
		if window is not None and window() :
			return window()
		
		window = _LocalJobsWindow( jobPool )
		jobPool._window = weakref.ref( window )
		
		return window