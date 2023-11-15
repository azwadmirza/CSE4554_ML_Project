    def _read_from_file(self, stream, format='json'):
        """
        Fill database from file, do not maintain old data
        Translate the spec portions from node-dict form to spec form

        Does not do any locking.
        """
        if format.lower() == 'json':
            load = sjson.load
        elif format.lower() == 'yaml':
            load = syaml.load
        else:
            raise ValueError("Invalid database format: %s" % format)

        try:
            if isinstance(stream, basestring):
                with open(stream, 'r') as f:
                    fdata = load(f)
            else:
                fdata = load(stream)
        except MarkedYAMLError as e:
            raise syaml.SpackYAMLError("error parsing YAML database:", str(e))
        except Exception as e:
            raise CorruptDatabaseError("error parsing database:", str(e))

        if fdata is None:
            return

        def check(cond, msg):
            if not cond:
                raise CorruptDatabaseError(
                    "Spack database is corrupt: %s" % msg, self._index_path)

        check('database' in fdata, "No 'database' attribute in YAML.")

        # High-level file checks
        db = fdata['database']
        check('installs' in db, "No 'installs' in YAML DB.")
        check('version' in db, "No 'version' in YAML DB.")

        installs = db['installs']

        # TODO: better version checking semantics.
        version = Version(db['version'])
        if version > _db_version:
            raise InvalidDatabaseVersionError(_db_version, version)
        elif version < _db_version:
            self.reindex(spack.store.layout)
            installs = dict((k, v.to_dict()) for k, v in self._data.items())

        def invalid_record(hash_key, error):
            msg = ("Invalid record in Spack database: "
                   "hash: %s, cause: %s: %s")
            msg %= (hash_key, type(e).__name__, str(e))
            raise CorruptDatabaseError(msg, self._index_path)

        # Build up the database in three passes:
        #
        #   1. Read in all specs without dependencies.
        #   2. Hook dependencies up among specs.
        #   3. Mark all specs concrete.
        #
        # The database is built up so that ALL specs in it share nodes
        # (i.e., its specs are a true Merkle DAG, unlike most specs.)

        # Pass 1: Iterate through database and build specs w/o dependencies
        data = {}
        for hash_key, rec in installs.items():
            try:
                # This constructs a spec DAG from the list of all installs
                spec = self._read_spec_from_dict(hash_key, installs)

                # Insert the brand new spec in the database.  Each
                # spec has its own copies of its dependency specs.
                # TODO: would a more immmutable spec implementation simplify
                #       this?
                data[hash_key] = InstallRecord.from_dict(spec, rec)

            except Exception as e:
                invalid_record(hash_key, e)

        # Pass 2: Assign dependencies once all specs are created.
        for hash_key in data:
            try:
                self._assign_dependencies(hash_key, installs, data)
            except Exception as e:
                invalid_record(hash_key, e)

        # Pass 3: Mark all specs concrete.  Specs representing real
        # installations must be explicitly marked.
        # We do this *after* all dependencies are connected because if we
        # do it *while* we're constructing specs,it causes hashes to be
        # cached prematurely.
        for hash_key, rec in data.items():
            rec.spec._mark_concrete()

        self._data = data