    def _set_pgrp(info):
        try:
            info['pgrp'] = os.getpgid(info['pids'][0])
        except ProcessLookupError:
            pass