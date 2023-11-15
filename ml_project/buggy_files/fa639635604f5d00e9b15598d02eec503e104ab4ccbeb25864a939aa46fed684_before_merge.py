    def _send_signal(job, signal):
        os.killpg(job['pgrp'], signal)