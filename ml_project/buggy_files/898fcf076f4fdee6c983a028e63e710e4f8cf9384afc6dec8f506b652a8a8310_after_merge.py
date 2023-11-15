    def requirement(self, package, formatted=False):
        if formatted and not package.source_type:
            req = "{}=={}".format(package.name, package.version)
            for h in package.hashes:
                hash_type = "sha256"
                if ":" in h:
                    hash_type, h = h.split(":")

                req += " --hash {}:{}".format(hash_type, h)

            req += "\n"

            return req

        if package.source_type in ["file", "directory"]:
            if package.root_dir:
                req = os.path.join(package.root_dir, package.source_url)
            else:
                req = os.path.realpath(package.source_url)

            if package.develop and package.source_type == "directory":
                req = ["-e", req]

            return req

        if package.source_type == "git":
            return "git+{}@{}#egg={}".format(
                package.source_url, package.source_reference, package.name
            )

        if package.source_type == "url":
            return "{}#egg={}".format(package.source_url, package.name)

        return "{}=={}".format(package.name, package.version)