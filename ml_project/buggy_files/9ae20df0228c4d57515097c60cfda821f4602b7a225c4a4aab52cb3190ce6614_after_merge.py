    def __contains__(self, other):
        # Split event into each subdomain
        for domain in self.domains:
            # Collect the parts of this event which associate to this domain
            elem = frozenset([item for item in other
                              if domain.symbols.contains(item[0]) == S.true])
            # Test this sub-event
            if elem not in domain:
                return False
        # All subevents passed
        return True