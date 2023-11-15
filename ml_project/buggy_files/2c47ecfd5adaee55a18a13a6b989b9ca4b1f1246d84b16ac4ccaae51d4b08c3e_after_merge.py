    def simplify(self):
        if self.reanalyzeable:
            self.retry_infer()
        elif self.promotions:
            self.resolve_promotion_cycles()
        else:
            # All dependencies are resolved, we are done
            pass

        self.is_resolved = True