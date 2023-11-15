    def replacements(self, creator, dest_folder):
        replacements = super(PythonActivator, self).replacements(creator, dest_folder)
        site_dump = json.dumps([os.path.relpath(str(i), str(dest_folder)) for i in creator.site_packages], indent=2)
        replacements.update({"__SITE_PACKAGES__": site_dump})
        return replacements