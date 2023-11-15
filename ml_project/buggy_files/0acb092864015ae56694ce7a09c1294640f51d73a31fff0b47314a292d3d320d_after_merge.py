    def parse_records(self):
        """Build the hierarchy of given directory records, and structure
        into Patient, Studies, Series, Images hierarchy.

        This is intended for initial read of file only,
        it will not reorganize correctly if records are changed.
        """

        # Define a helper function for organizing the records
        def get_siblings(record, map_offset_to_record):
            """Return a list of all siblings of the given directory record,
            including itself.
            """
            sibling_list = [record]
            current_record = record
            while ('OffsetOfTheNextDirectoryRecord' in current_record and
                   current_record.OffsetOfTheNextDirectoryRecord):
                offset_of_next = current_record.OffsetOfTheNextDirectoryRecord
                sibling = map_offset_to_record[offset_of_next]
                sibling_list.append(sibling)
                current_record = sibling
            return sibling_list

        # Build the mapping from file offsets to records
        records = self.DirectoryRecordSequence
        if not records:
            return

        map_offset_to_record = {}
        for record in records:
            offset = record.seq_item_tell
            map_offset_to_record[offset] = record
        # logging.debug("Record offsets: " + map_offset_to_record.keys())

        # Find the children of each record
        for record in records:
            record.children = []
            if 'OffsetOfReferencedLowerLevelDirectoryEntity' in record:
                child_offset = (record.
                                OffsetOfReferencedLowerLevelDirectoryEntity)
                if child_offset:
                    child = map_offset_to_record[child_offset]
                    record.children = get_siblings(child, map_offset_to_record)

        self.patient_records = [
            record for record in records
            if getattr(record, 'DirectoryRecordType') == 'PATIENT'
        ]