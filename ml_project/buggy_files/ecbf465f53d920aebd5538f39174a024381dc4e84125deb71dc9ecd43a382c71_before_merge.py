    def close(self):
        if self.json:
            sys.stdout.write('{"fetch":"%s","finished":true,"maxval":1,"progress":1}\n\0'
                             % self.description)
            sys.stdout.flush()
        elif self.enabled:
            self.pbar.close()
        self.enabled = False