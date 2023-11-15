    def __init__( self, files_dir=None, job_wrapper=None, job_id=None, job_file=None, output_file=None, error_file=None, exit_code_file=None, job_name=None, job_destination=None  ):
        super( AsynchronousJobState, self ).__init__( job_wrapper, job_destination )
        self.old_state = None
        self._running = False
        self.check_count = 0
        self.start_time = None

        # job_id is the DRM's job id, not the Galaxy job id
        self.job_id = job_id

        self.job_file = job_file
        self.output_file = output_file
        self.error_file = error_file
        self.exit_code_file = exit_code_file
        self.job_name = job_name

        self.set_defaults( files_dir )

        self.cleanup_file_attributes = [ 'job_file', 'output_file', 'error_file', 'exit_code_file' ]