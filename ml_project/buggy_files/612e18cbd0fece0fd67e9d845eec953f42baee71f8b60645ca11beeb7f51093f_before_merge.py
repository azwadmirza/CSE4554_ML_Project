    def save_attribs(self):
        set_attrib_file(
            self.workpath, (self.cat, self.pp, self.script, self.priority, self.final_name, self.password, self.url)
        )