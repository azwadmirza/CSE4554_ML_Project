    def replacements(self, creator, dest_folder):
        replacements = super(PythonActivator, self).replacements(creator, dest_folder)
        site_dump = json.dumps(list({os.path.relpath(str(i), str(dest_folder)) for i in creator.libs}), indent=2)
        replacements.update({"__SITE_PACKAGES__": site_dump})
        return replacements