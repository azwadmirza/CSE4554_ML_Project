    def _check_name_map(self, name_map):
        """Check `name_map` follows the correct format."""
        # Check section option paris are not repeated
        sections_options = []
        for _, sec_opts in name_map.items():
            for section, options in sec_opts:
                for option in options:
                    sec_opt = (section, option)
                    if sec_opt not in sections_options:
                        sections_options.append(sec_opt)
                    else:
                        error_msg = (
                            'Different files are holding the same '
                            'section/option: "{}/{}"!'.format(section, option)
                        )
                        raise ValueError(error_msg)
        return name_map