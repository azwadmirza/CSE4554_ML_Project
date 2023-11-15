    def cleanup( self ):
        for file in [ getattr( self, a ) for a in self.cleanup_file_attributes if hasattr( self, a ) ]:
            try:
                os.unlink( file )
            except Exception as e:
                # TODO: Move this prefix stuff to a method so we don't have dispatch on attributes we may or may
                # not have.
                if not hasattr( self, "job_id" ):
                    prefix = "(%s)" % self.job_wrapper.get_id_tag()
                else:
                    prefix = "(%s/%s)" % ( self.job_wrapper.get_id_tag(), self.job_id )
                log.debug( "%s Unable to cleanup %s: %s" % (prefix, file, str( e ) ) )