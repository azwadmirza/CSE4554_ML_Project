    def run_command(command):
        """Runs a monit command, and returns the new status."""
        module.run_command('%s %s %s' % (MONIT, command, name), check_rc=True)
        return get_status()