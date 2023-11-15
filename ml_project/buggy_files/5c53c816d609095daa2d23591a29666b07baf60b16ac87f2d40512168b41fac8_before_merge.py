    def run(self):
        logger.info(os.path.relpath(Repo.find_root()))
        return 0