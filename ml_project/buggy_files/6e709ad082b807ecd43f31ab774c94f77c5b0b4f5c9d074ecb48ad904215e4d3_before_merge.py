    def _failed_compile(msg):
        log.error(msg)
        ret.setdefault('errors', {})[short_path_name] = [msg]
        return False