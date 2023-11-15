    def prepare_models(self, engine):
        if not self.prepared:
            # SQLAlchemy will check if the items exist before trying to
            # create them, which is a race condition. If it raises an error
            # in one iteration, the next may pass all the existence checks
            # and the call will succeed.
            retries = 0
            while True:
                try:
                    ResultModelBase.metadata.create_all(engine)
                except DatabaseError:
                    if retries < PREPARE_MODELS_MAX_RETRIES:
                        sleep_amount_ms = get_exponential_backoff_interval(
                            10, retries, 1000, True
                        )
                        time.sleep(sleep_amount_ms / 1000)
                        retries += 1
                    else:
                        raise
                else:
                    break
            self.prepared = True