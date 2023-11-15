    def cleanup( self ):
        for file in [ getattr( self, a ) for a in self.cleanup_file_attributes if hasattr( self, a ) ]:
            try:
                os.unlink( file )
            except Exception as e:
                log.debug( "(%s/%s) Unable to cleanup %s: %s" % ( self.job_wrapper.get_id_tag(), self.job_id, file, str( e ) ) )