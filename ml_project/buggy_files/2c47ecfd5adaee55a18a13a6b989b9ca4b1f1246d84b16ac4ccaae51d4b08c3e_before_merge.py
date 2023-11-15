    def simplify(self):
        if self.reanalyzeable:
            self.retry_infer()
        elif self.promotions:
            self.resolve_promotion_cycles()
        else:
            assert False

        self.is_resolved = True