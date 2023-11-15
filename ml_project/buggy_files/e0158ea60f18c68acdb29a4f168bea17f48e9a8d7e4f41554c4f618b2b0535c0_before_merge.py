    def apply_files_filter(self, frame, filename, force_check_project_scope):
        '''
        Should only be called if `self.is_files_filter_enabled == True`.

        Note that it covers both the filter by specific paths includes/excludes as well
        as the check which filters out libraries if not in the project scope.

        :param force_check_project_scope:
            Check that the file is in the project scope even if the global setting
            is off.

        :return bool:
            True if it should be excluded when stepping and False if it should be
            included.
        '''
        cache_key = (frame.f_code.co_firstlineno, filename, force_check_project_scope, frame.f_code)
        try:
            return self._apply_filter_cache[cache_key]
        except KeyError:
            if self.plugin is not None and (self.has_plugin_line_breaks or self.has_plugin_exception_breaks):
                # If it's explicitly needed by some plugin, we can't skip it.
                if not self.plugin.can_skip(self, frame):
                    pydev_log.debug_once('File traced (included by plugins): %s', filename)
                    self._apply_filter_cache[cache_key] = False
                    return False

            if self._exclude_filters_enabled:
                exclude_by_filter = self._exclude_by_filter(frame, filename)
                if exclude_by_filter is not None:
                    if exclude_by_filter:
                        # ignore files matching stepping filters
                        pydev_log.debug_once('File not traced (excluded by filters): %s', filename)

                        self._apply_filter_cache[cache_key] = True
                        return True
                    else:
                        pydev_log.debug_once('File traced (explicitly included by filters): %s', filename)

                        self._apply_filter_cache[cache_key] = False
                        return False

            if (self._is_libraries_filter_enabled or force_check_project_scope) and not self.in_project_scope(frame):
                # ignore library files while stepping
                self._apply_filter_cache[cache_key] = True
                if force_check_project_scope:
                    pydev_log.debug_once('File not traced (not in project): %s', filename)
                else:
                    pydev_log.debug_once('File not traced (not in project - force_check_project_scope): %s', filename)

                return True

            if force_check_project_scope:
                pydev_log.debug_once('File traced: %s (force_check_project_scope)', filename)
            else:
                pydev_log.debug_once('File traced: %s', filename)
            self._apply_filter_cache[cache_key] = False
            return False