    def get_pool(self, num=None):
        """Gets a pool of workers to do some parallel work.

        pool will be cached, which implies that one should be very clear how
        many processes one needs, as it's allocated at most once. Subsequent
        calls of get_pool() will reuse the cached pool.

        Args:
            num(int): Number of workers one needs.
        Returns:
            pool(multiprocessing.Pool): A pool of workers.
        """
        processes = self.get_processes(num or self.processes)
        logging.info("Calling multiprocessing.Pool(%d)", processes)
        return multiprocessing.Pool(processes)