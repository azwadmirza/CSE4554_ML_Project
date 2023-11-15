    def _set_pgrp(info):
        pid = info['pids'][0]
        if pid is None:
            # occurs if first process is an alias
            info['pgrp'] = None
            return
        try:
            info['pgrp'] = os.getpgid(pid)
        except ProcessLookupError:
            info['pgrp'] = None