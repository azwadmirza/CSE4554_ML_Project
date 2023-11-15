    def add_to_index(self, unit, source=True):
        '''
        Updates/Adds to all indices given unit.
        '''
        if settings.OFFLOAD_INDEXING:
            from weblate.trans.models import IndexUpdate
            IndexUpdate.objects.get_or_create(unit=unit, source=source)
            return

        writer_target = FULLTEXT_INDEX.target_writer(
            unit.translation.language.code
        )
        writer_source = FULLTEXT_INDEX.source_writer()

        if source:
            self.add_to_source_index(
                unit.checksum,
                unit.source,
                unit.context,
                writer_source)
        self.add_to_target_index(
            unit.checksum,
            unit.target,
            writer_target)