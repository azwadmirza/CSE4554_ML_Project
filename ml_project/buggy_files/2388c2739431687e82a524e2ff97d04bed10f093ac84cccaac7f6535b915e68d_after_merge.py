    def _status(self):
        """Update the resource dictionary with job statuses."""

        job_id_list = ' '.join(self.resources.keys())
        cmd = "condor_q {0} -af:jr JobStatus".format(job_id_list)
        retcode, stdout, stderr = self.execute_wait(cmd)
        """
        Example output:

        $ condor_q 34524642.0 34524643.0 -af:jr JobStatus
        34524642.0 2
        34524643.0 1
        """

        for line in stdout.splitlines():
            parts = line.strip().split()
            job_id = parts[0]
            status = translate_table.get(parts[1], 'UNKNOWN')
            self.resources[job_id]['status'] = status