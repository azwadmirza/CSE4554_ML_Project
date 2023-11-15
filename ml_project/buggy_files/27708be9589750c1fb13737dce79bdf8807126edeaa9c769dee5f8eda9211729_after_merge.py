    def game_exe(self):
        """Return the game's executable's path."""
        exe = self.game_config.get("exe")
        if not exe:
            return
        if os.path.isabs(exe):
            return exe
        if self.game_path:
            return os.path.join(self.game_path, exe)
        return system.find_executable(exe)