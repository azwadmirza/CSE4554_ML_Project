    def _storeObjects(self, storable_objects):

        for (source, destination, filename) in storable_objects:

            self.sections["transfers"][destination].close()
            self.sections["transfers"][destination] = shelve.open(os.path.join(self.data_dir, filename), flag='n')

            for (key, value) in source.items():
                self.sections["transfers"][destination][key] = value