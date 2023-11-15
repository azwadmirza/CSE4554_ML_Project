    def update_to(self, fraction):
        if self.json:
            sys.stdout.write('{"fetch":"%s","finished":false,"maxval":1,"progress":%f}\n\0'
                             % (self.description, fraction))
        elif self.enabled:
            self.pbar.update(fraction - self.pbar.n)