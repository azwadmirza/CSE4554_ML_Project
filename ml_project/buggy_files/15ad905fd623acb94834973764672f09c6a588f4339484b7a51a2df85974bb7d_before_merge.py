    def observe(self) -> defer.Deferred:
        """Observe the underlying deferred.

        This returns a brand new deferred that is resolved when the underlying
        deferred is resolved. Interacting with the returned deferred does not
        effect the underdlying deferred.
        """
        if not self._result:
            d = defer.Deferred()

            def remove(r):
                self._observers.discard(d)
                return r

            d.addBoth(remove)

            self._observers.add(d)
            return d
        else:
            success, res = self._result
            return defer.succeed(res) if success else defer.fail(res)