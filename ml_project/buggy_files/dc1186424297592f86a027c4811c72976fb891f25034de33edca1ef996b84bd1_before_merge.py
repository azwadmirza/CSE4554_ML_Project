	def acquire( jobPool ) :
		
		assert( isinstance( jobPool, Gaffer.LocalDispatcher.JobPool ) )
		
		window = getattr( jobPool, "_window", None )
		if window :
			return window
		
		window = _LocalJobsWindow( jobPool )
		jobPool._window = window
		
		return window