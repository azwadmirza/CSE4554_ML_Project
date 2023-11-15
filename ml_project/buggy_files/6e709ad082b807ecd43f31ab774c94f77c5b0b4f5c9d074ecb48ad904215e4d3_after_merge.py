    def _failed_compile(prefix_msg, error_msg):
        log.error('{0} \'{1}\': {2} '.format(prefix_msg, short_path_name, error_msg))
        ret.setdefault('errors', {})[short_path_name] = ['{0}, {1} '.format(prefix_msg, error_msg)]
        return False