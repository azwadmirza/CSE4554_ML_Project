    def get_value(self, series, key):
        # somewhat broken encapsulation
        from pandas.core.indexing import maybe_droplevels
        from pandas.core.series import Series

        # Label-based
        s = _values_from_object(series)
        k = _values_from_object(key)

        def _try_mi(k):
            # TODO: what if a level contains tuples??
            loc = self.get_loc(k)
            new_values = series._values[loc]
            new_index = self[loc]
            new_index = maybe_droplevels(new_index, k)
            return Series(new_values, index=new_index, name=series.name)

        try:
            return self._engine.get_value(s, k)
        except KeyError as e1:
            try:
                return _try_mi(key)
            except KeyError:
                pass

            try:
                return _index.get_value_at(s, k)
            except IndexError:
                raise
            except TypeError:
                # generator/iterator-like
                if is_iterator(key):
                    raise InvalidIndexError(key)
                else:
                    raise e1
            except Exception:  # pragma: no cover
                raise e1
        except TypeError:

            # a Timestamp will raise a TypeError in a multi-index
            # rather than a KeyError, try it here
            # note that a string that 'looks' like a Timestamp will raise
            # a KeyError! (GH5725)
            if (isinstance(key, (datetime.datetime, np.datetime64)) or
                    (compat.PY3 and isinstance(key, compat.string_types))):
                try:
                    return _try_mi(key)
                except (KeyError):
                    raise
                except:
                    pass

                try:
                    return _try_mi(Timestamp(key))
                except:
                    pass

            raise InvalidIndexError(key)