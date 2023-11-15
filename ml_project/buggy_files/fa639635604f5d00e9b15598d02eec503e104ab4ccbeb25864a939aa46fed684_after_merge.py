    def _send_signal(job, signal):
        pgrp = job['pgrp']
        if pgrp is None:
            for pid in job['pids']:
                try:
                    os.kill(pid, signal)
                except:
                    pass
        else:
            os.killpg(job['pgrp'], signal)