    def classify(self, post, lang):
        """Classify the given post for the given language."""
        destpath = post.destination_path(lang, sep='/')
        index_len = len(self.site.config["INDEX_FILE"])
        if destpath[-(1 + index_len):] == '/' + self.site.config["INDEX_FILE"]:
            destpath = destpath[:-(1 + index_len)]
        i = destpath.rfind('/')
        return destpath[:i] if i >= 0 else ''