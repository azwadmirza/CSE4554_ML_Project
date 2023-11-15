    def init_config(self):
        '''Init docutils settings.'''
        ds = {}
        gc = self.c.config

        def getConfig(getfun, name, default, setfun=None, setvar=None):
            """Make a shorthand way to get and store a setting with defaults"""
            r = getfun('vr_' + name) # keep docutils name but prefix
            if setfun: # settings are held in Qactions
                if r: setfun(r)
                else: setfun(default)
            elif setvar: # Just setting a variable
                if r: setvar = r
                else: setvar = default
            else: # settings held in dict (for docutils use)
                if r: ds[name] = r
                else: ds[name] = default
        # Do docutils config (note that the vr_ prefix is omitted)

        getConfig(gc.getString, 'stylesheet_path', '')
        getConfig(gc.getInt, 'halt_level', 6)
        getConfig(gc.getInt, 'report_level', 5)
        getConfig(gc.getString, 'math_output', 'mathjax')
        getConfig(gc.getBool, 'smart_quotes', True)
        getConfig(gc.getBool, 'embed_stylesheet', True)
        getConfig(gc.getBool, 'xml_declaration', False)
        # Additional docutils values suggested by T P <wingusr@gmail.com>
        getConfig(gc.getString, 'syntax_highlight', 'long')
        getConfig(gc.getBool, 'no_compact_lists', False)
        getConfig(gc.getBool, 'no_compact_field_lists', False)
        # Do VR2 init values
        getConfig(gc.getBool, 'verbose', False, self.verbose_mode_action.setChecked)
        getConfig(gc.getBool, 'tree_mode', False, self.tree_mode_action.setChecked)
        getConfig(gc.getBool, 'auto_update', True, self.auto_mode_action.setChecked)
        getConfig(gc.getBool, 'lock_node', False, self.lock_mode_action.setChecked)
        getConfig(gc.getBool, 'slideshow', False, self.slideshow_mode_action.setChecked)
        getConfig(gc.getBool, 'visible_code', True, self.visible_code_action.setChecked)
        getConfig(gc.getBool, 'execute_code', False, self.execute_code_action.setChecked)
        getConfig(gc.getBool, 'rest_code_output', False, self.reST_code_action.setChecked)
        # Misc other internal settings
        # Mark of the Web (for IE) to allow sensible security options
        #getConfig(gc.getBool, 'include_MOTW', True, setvar=self.MOTW)
        return ds