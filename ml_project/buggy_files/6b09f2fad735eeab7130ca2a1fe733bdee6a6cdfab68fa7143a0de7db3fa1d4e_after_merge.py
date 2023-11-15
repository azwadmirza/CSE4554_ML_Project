    def launch_install(self, script_index):
        script = self.scripts[script_index]
        self.interpreter = installer.ScriptInterpreter(script, self)
        game_name = self.interpreter.game_name.replace('&', '&amp;')
        self.title_label.set_markup(u"<b>Installing {}</b>".format(game_name))
        self.continue_install()