    def _pkg_is_installed(pkg, installed_pkgs):
        '''
        Helper function to determine if a package is installed

        This performs more complex comparison than just checking
        keys, such as examining source repos to see if the package
        was installed by a different name from the same repo

        :pkg str: The package to compare
        :installed_pkgs: A dictionary produced by npm list --json
        '''
        if (pkg_name in installed_pkgs and
            'version' in installed_pkgs[pkg_name]):
            return True
        # Check to see if we are trying to install from a URI
        elif '://' in pkg_name:  # TODO Better way?
            for pkg_details in installed_pkgs.values():
                pkg_from = pkg_details.get('from', '').split('://')[1]
                if pkg_name.split('://')[1] == pkg_from:
                    return True
        return False