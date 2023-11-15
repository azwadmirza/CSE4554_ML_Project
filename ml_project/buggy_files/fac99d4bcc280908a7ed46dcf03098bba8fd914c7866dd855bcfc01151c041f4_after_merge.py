    def ensure_directories(self):
        return {self.dest_dir, self.bin_dir, self.script_dir, self.stdlib} | set(self.libs)