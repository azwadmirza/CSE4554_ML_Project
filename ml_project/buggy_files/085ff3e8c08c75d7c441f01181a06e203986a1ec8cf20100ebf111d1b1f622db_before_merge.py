        def thd(engine):
            # if the migrate_version table exists, we can just let migrate
            # take care of this process.
            if table_exists(engine, 'migrate_version'):
                r = engine.execute(
                    "select version from migrate_version limit 1")
                old_version = r.scalar()
                if old_version < 40:
                    raise EightUpgradeError()
                upgrade(engine)

            # if the version table exists, then we can version_control things
            # at that version, drop the version table, and let migrate take
            # care of the rest.
            elif table_exists(engine, 'version'):
                raise EightUpgradeError()

            # otherwise, this db is new, so we don't bother using the migration engine
            # and just create the tables, and put the version directly to
            # latest
            else:
                # do some tests before getting started
                test_unicode(engine)

                log.msg("Initializing empty database")
                Model.metadata.create_all(engine)
                repo = migrate.versioning.repository.Repository(self.repo_path)

                version_control(engine, repo.latest)