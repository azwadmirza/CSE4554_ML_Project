    def game_exe(self):
        """Return the game's executable's path."""
        exe = self.game_config.get("exe")
        if exe:
            if os.path.isabs(exe):
                exe_path = exe
            else:
                exe_path = os.path.join(self.game_path, exe)
            return exe_path