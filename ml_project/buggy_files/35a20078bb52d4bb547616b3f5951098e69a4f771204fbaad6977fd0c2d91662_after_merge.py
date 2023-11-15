    def start_hatching(self, locust_count=None, hatch_rate=None, wait=False):
        if hatch_rate > 100:
            logger.warning("Your selected hatch rate is very high (>100), and this is known to sometimes cause issues. Do you really need to ramp up that fast?")
        self.hatching_greenlet = gevent.spawn(lambda: super(LocalLocustRunner, self).start_hatching(locust_count, hatch_rate, wait=wait))
        self.greenlet = self.hatching_greenlet