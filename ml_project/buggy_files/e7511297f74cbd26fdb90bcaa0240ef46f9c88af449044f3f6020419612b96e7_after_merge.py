    def __init__( self, job_wrapper, job_destination ):
        self.runner_state_handled = False
        self.job_wrapper = job_wrapper
        self.job_destination = job_destination

        self.cleanup_file_attributes = [ 'job_file', 'output_file', 'error_file', 'exit_code_file' ]