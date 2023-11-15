    def gen_setup(self, filename, fragment, tmpdir):
        match = EGG_FRAGMENT.match(fragment)
        dists = match and [
            d for d in
            interpret_distro_name(filename, match.group(1), None) if d.version
        ] or []

        if len(dists) == 1:  # unambiguous ``#egg`` fragment
            basename = os.path.basename(filename)

            # Make sure the file has been downloaded to the temp dir.
            if os.path.dirname(filename) != tmpdir:
                dst = os.path.join(tmpdir, basename)
                from pex.third_party.setuptools.command.easy_install import samefile
                if not samefile(filename, dst):
                    shutil.copy2(filename, dst)
                    filename = dst

            with open(os.path.join(tmpdir, 'setup.py'), 'w') as file:
                file.write(
                    "from setuptools import setup\n"
                    "setup(name=%r, version=%r, py_modules=[%r])\n"
                    % (
                        dists[0].project_name, dists[0].version,
                        os.path.splitext(basename)[0]
                    )
                )
            return filename

        elif match:
            raise DistutilsError(
                "Can't unambiguously interpret project/version identifier %r; "
                "any dashes in the name or version should be escaped using "
                "underscores. %r" % (fragment, dists)
            )
        else:
            raise DistutilsError(
                "Can't process plain .py files without an '#egg=name-version'"
                " suffix to enable automatic setup script generation."
            )