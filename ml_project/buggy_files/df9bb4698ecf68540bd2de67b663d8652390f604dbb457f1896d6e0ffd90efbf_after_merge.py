    def fixup_python2(self):
        """Perform operations needed to make the created environment work on Python 2"""
        for module in self.modules():
            self.add_module(module)
        # 2. install a patched site-package, the default Python 2 site.py is not smart enough to understand pyvenv.cfg,
        # so we inject a small shim that can do this
        site_py = self.stdlib / "site.py"
        custom_site = get_custom_site()
        if IS_ZIPAPP:
            custom_site_text = read_from_zipapp(custom_site)
        else:
            custom_site_text = custom_site.read_text()
        expected = json.dumps(
            [os.path.relpath(six.ensure_text(str(i)), six.ensure_text(str(site_py))) for i in self.libs]
        )
        site_py.write_text(custom_site_text.replace("___EXPECTED_SITE_PACKAGES___", expected))