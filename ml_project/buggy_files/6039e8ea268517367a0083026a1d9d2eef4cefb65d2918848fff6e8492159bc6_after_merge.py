    def init_dicts(self, contigs_db_path, split_names_of_interest=set([])):
        """Initialize essential data for HMM stuff.

           This function will do its best to not load any data that will not
           be used later for HMM related operations. For instance, it will
           learn which gene caller ids are of interest based on HMM sources,
           and only recover data for splits and contigs based on that information,
           not accessing a large fraction of a given contigs database.
        """

        utils.is_contigs_db(contigs_db_path)
        contigs_db = db.DB(contigs_db_path, anvio.__contigs__version__, run=self.run, progress=self.progress)
        self.hmm_hits_info = contigs_db.get_table_as_dict(t.hmm_hits_info_table_name)

        missing_sources = [s for s in self.sources if s not in self.hmm_hits_info]
        if len(missing_sources):
            contigs_db.disconnect()
            progress.reset()
            raise ConfigError("Bad news, Houston :/ The contigs database '%s' is missing one or more HMM sources "
                              "that you wished it didn't: '%s'." % (contigs_db_path, ', '.join(missing_sources)))

        if not self.sources:
            self.sources = set(list(self.hmm_hits_info.keys()))

        if not self.sources:
            # there is nothing to initialize..
            return

        self.progress.new("Recovering sequences for HMM Hits")
        self.progress.update('...')

        # get data from HMM tables based on sources of interest
        self.progress.update('Getting data from HMM tables for %d source(s)' % len(self.sources))
        where_clause_for_sources = "source in (%s)" % ', '.join(['"%s"' % s for s in self.sources])
        self.hmm_hits = contigs_db.get_some_rows_from_table_as_dict(t.hmm_hits_table_name,
                                                                    where_clause=where_clause_for_sources,
                                                                    error_if_no_data=False)
        self.hmm_hits_splits = contigs_db.get_some_rows_from_table_as_dict(t.hmm_hits_splits_table_name,
                                                                    where_clause=where_clause_for_sources,
                                                                    error_if_no_data=False)

        # if the user sent a split names of interest, it means they are interested in hits that only occur
        # in a specific set of split names. NOTE: this really makes it very difficult to deal with HMM hits
        # that span through multiple splits. here we will mark such HMM hits in `hmm_hits_splits_entry_ids_to_remove`
        # for removal, but we will also keep track of those guys and let the user know what happened.
        if len(split_names_of_interest):
            total_num_split_names = len(set(self.hmm_hits_splits[entry_id]['split'] for entry_id in self.hmm_hits_splits))
            hmm_hits_splits_entry_ids_to_remove = set([])
            hmm_hits_entry_ids_to_remove = set([])
            hmm_hits_entry_ids_associated_with_fragmented_hmm_hits = set([])
            hmm_sources_associated_with_fragmented_hmm_hits = set([])
            for entry_id in self.hmm_hits_splits:
                if self.hmm_hits_splits[entry_id]['split'] not in split_names_of_interest:
                    hmm_hits_splits_entry_ids_to_remove.add(entry_id)
                    hmm_hits_entry_ids_to_remove.add(self.hmm_hits_splits[entry_id]['hmm_hit_entry_id'])

                    if not self.hmm_hits_splits[entry_id]['percentage_in_split'] == 100:
                        # this is important. if we are here, there is a bit more to do since it means that
                        # the split name associated with self.hmm_hits_splits[entry_id] is not in
                        # `split_names_of_interest`. but since the `percentage_in_split` for this HMM hit is NOT
                        # 100%, it could be the case that other splits that contain pieces of this HMM hit may
                        # still be in `split_names_of_interest`. But here we are setting the stage for this
                        # HMM hit to be removed from `self.hmm_hits` altogether. To make things right, we must
                        # go through `hmm_hits_splits`, and remove remaining entries there that is associated with
                        # this HMM hit later using the contents of this variable:
                        hmm_hits_entry_ids_associated_with_fragmented_hmm_hits.add(self.hmm_hits_splits[entry_id]['hmm_hit_entry_id'])
                        hmm_sources_associated_with_fragmented_hmm_hits.add(self.hmm_hits_splits[entry_id]['source'])

            if len(hmm_hits_entry_ids_associated_with_fragmented_hmm_hits):
                # if we are here, we will have to update `hmm_hits_splits_entry_ids_to_remove` carefully:
                additional_entry_ids_to_be_removed = set([e for e in self.hmm_hits_splits if self.hmm_hits_splits[e]['hmm_hit_entry_id'] in hmm_hits_entry_ids_associated_with_fragmented_hmm_hits])
                hmm_hits_splits_entry_ids_to_remove.update(additional_entry_ids_to_be_removed)

            if len(hmm_hits_splits_entry_ids_to_remove):
                for entry_id in hmm_hits_splits_entry_ids_to_remove:
                    self.hmm_hits_splits.pop(entry_id)

            if len(hmm_hits_entry_ids_to_remove):
                for entry_id in hmm_hits_entry_ids_to_remove:
                    self.hmm_hits.pop(entry_id)

            filtered_num_split_names = len(set(self.hmm_hits_splits[entry_id]['split'] for entry_id in self.hmm_hits_splits))

            if anvio.DEBUG:
                self.progress.end()

                self.run.warning(None, header="SequencesForHMMHits info")
                self.run.info_single('%d split names of interest are found' % len(split_names_of_interest))
                self.run.info('Total split names w/HMM hits', total_num_split_names)
                self.run.info('Final split names w/HMM hits', filtered_num_split_names, nl_after=1)

                self.progress.new("Recovering sequences for HMM Hits")
                self.progress.update('...')

        if not len(self.hmm_hits):
            # there are HMMs but no hits. FINE.
            self.progress.end()
            contigs_db.disconnect()
            return

        gene_caller_ids_of_interest = set([e['gene_callers_id'] for e in self.hmm_hits.values()])
        where_clause_for_genes = "gene_callers_id in (%s)" % ', '.join(['%d' % g for g in gene_caller_ids_of_interest])

        self.progress.update('Recovering split and contig names for %d genes' % (len(gene_caller_ids_of_interest)))
        split_names_of_interest, contig_names_of_interest = utils.get_split_and_contig_names_of_interest(contigs_db_path, gene_caller_ids_of_interest)

        self.progress.update('Recovering contig seqs for %d genes' % (len(gene_caller_ids_of_interest)))
        where_clause_for_contigs = "contig in (%s)" % ', '.join(['"%s"' % s for s in contig_names_of_interest])
        self.contig_sequences = contigs_db.get_some_rows_from_table_as_dict(t.contig_sequences_table_name, \
                                                                            string_the_key=True, \
                                                                            where_clause=where_clause_for_contigs)

        self.progress.update('Recovering amino acid seqs for %d genes' % (len(gene_caller_ids_of_interest)))
        self.aa_sequences = contigs_db.get_some_rows_from_table_as_dict(t.gene_amino_acid_sequences_table_name, \
                                                                        where_clause=where_clause_for_genes)

        self.genes_in_contigs = contigs_db.get_some_rows_from_table_as_dict(t.genes_in_contigs_table_name, \
                                                                            where_clause=where_clause_for_genes)

        self.splits_in_contigs = list(split_names_of_interest)

        self.progress.end()
        contigs_db.disconnect()