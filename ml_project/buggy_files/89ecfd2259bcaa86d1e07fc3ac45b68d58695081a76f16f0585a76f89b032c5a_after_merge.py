    def env_vars_as_dict(self, logger: Optional[object] = None) -> Dict:
        """Operation stores environment variables in a list of name=value pairs, while
           subprocess.run() requires a dictionary - so we must convert.  If no envs are
           configured on the Operation, the existing env is returned, otherwise envs
           configured on the Operation are overlayed on the existing env.
        """
        envs = {}
        for nv in self.env_vars:
            if len(nv) > 0:
                nv_pair = nv.split("=")
                if len(nv_pair) == 2:
                    envs[nv_pair[0]] = nv_pair[1]
                else:
                    if logger:
                        logger.warning(f"Could not process environment variable entry `{nv}`, skipping...")
                    else:
                        print(f"Could not process environment variable entry `{nv}`, skipping...")
        return envs