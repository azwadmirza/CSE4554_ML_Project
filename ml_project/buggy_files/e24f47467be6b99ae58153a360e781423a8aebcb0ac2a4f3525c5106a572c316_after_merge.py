    def do_contigs_db(self):
        self.progress.new('Splitting "%s"' % self.bin_id)
        self.progress.update('Subsetting the contigs database')

        bin_contigs_db = dbops.ContigsDatabase(self.bin_contigs_db_path)
        bin_contigs_db.touch()

        # copy-paste tables that will largely stay the same from the parent
        bin_contigs_db.db.copy_paste(table_name='self', source_db_path=self.contigs_db_path)
        bin_contigs_db.db.copy_paste(table_name='hmm_hits_info', source_db_path=self.contigs_db_path)
        bin_contigs_db.db.copy_paste(table_name='taxon_names', source_db_path=self.contigs_db_path)

        # update some variables in the self table:
        self.contigs_db_hash = bin_contigs_db.get_hash()
        bin_contigs_db.db.update_meta_value('num_contigs', self.num_contigs)
        bin_contigs_db.db.update_meta_value('num_splits', self.num_splits)
        bin_contigs_db.db.update_meta_value('total_length', self.total_length)
        bin_contigs_db.db.update_meta_value('creation_date', bin_contigs_db.get_date())
        bin_contigs_db.db.update_meta_value('contigs_db_hash', self.contigs_db_hash)
        bin_contigs_db.db.update_meta_value('project_name', self.bin_id)

        # the empty contigs db is ready
        bin_contigs_db.disconnect()

        # touch does not create the k-mers tables, so the resulting contigs db is missing them. we
        # will add them to the db here.
        bin_contigs_db = dbops.ContigsDatabase(self.bin_contigs_db_path)
        k = KMerTablesForContigsAndSplits(None, k=bin_contigs_db.meta['kmer_size'])
        for table_name in ['kmer_contigs', 'kmer_splits']:
            bin_contigs_db.db.create_table(table_name, k.kmers_table_structure, k.kmers_table_types)
        bin_contigs_db.disconnect()

        # setup the filtering rules for migrating data:
        tables = {
                    t.contig_sequences_table_name: ('contig', self.contig_names),
                    t.contigs_info_table_name: ('contig', self.contig_names),
                    t.gene_function_calls_table_name: ('gene_callers_id', self.gene_caller_ids),
                    t.gene_amino_acid_sequences_table_name: ('gene_callers_id', self.gene_caller_ids),
                    t.genes_in_contigs_table_name: ('gene_callers_id', self.gene_caller_ids),
                    t.genes_in_splits_table_name: ('gene_callers_id', self.gene_caller_ids),
                    t.genes_taxonomy_table_name: ('gene_callers_id', self.gene_caller_ids),
                    t.hmm_hits_table_name: ('gene_callers_id', self.gene_caller_ids),
                    t.hmm_hits_splits_table_name: ('split', self.split_names),
                    t.splits_info_table_name: ('split', self.split_names),
                    t.splits_taxonomy_table_name: ('split', self.split_names),
                    t.nt_position_info_table_name: ('contig_name', self.contig_names),
                    t.scg_taxonomy_table_name: ('gene_callers_id', self.gene_caller_ids),
                    'kmer_contigs': ('contig', self.split_names),
                    'kmer_splits': ('contig', self.split_names),
                }

        self.migrate_data(tables, self.contigs_db_path, self.bin_contigs_db_path)

        # We're done here in theroy, but there is one more thing to do due to reasons partially explained in
        # issue https://github.com/merenlab/anvio/issues/1593 and PR https://github.com/merenlab/anvio/pull/1595.
        # The solution presented in the PR does not apply to split projects. so here we will calculate
        # what percentage of HMM hits are in splits described in this bin, and remove those that are less
        # than 100%.
        bin_contigs_db = dbops.ContigsDatabase(self.bin_contigs_db_path)
        hmm_hits_in_splits_dict = bin_contigs_db.db.get_table_as_dict(t.hmm_hits_splits_table_name)

        # the purpose of the folloing dict is to keep track of what total percentage of a given HMM hit is
        # described by all contig splits involved in this bin
        hmm_hits_id_percentage_described_dict = Counter({})
        for entry in hmm_hits_in_splits_dict.values():
            hmm_hits_id_percentage_described_dict[entry['hmm_hit_entry_id']] += entry['percentage_in_split']

        # now the `hmm_hits_id_percentage_described_dict` looks like this:
        #
        #   {2: 100, 3: 100.0, 5: 90.86727989487517, 6: 99.99999999999999, 4: 63.99858956276446}
        #
        # HMM hit ids that need to be cleared out from th `hmm_hits_in_splits` table is clear: 5 and 4, in this
        # example. But the problem is, due floating point logistics, in some cases things are not quite 100%,
        # although in reality they are, hence the need for `round`ing the percentages below.
        hmm_hit_ids_to_delete = [hit_id for hit_id in hmm_hits_id_percentage_described_dict if round(hmm_hits_id_percentage_described_dict[hit_id]) < 100]
        where_clause = f"hmm_hit_entry_id IN ({','.join([str(i) for i in hmm_hit_ids_to_delete])})"
        bin_contigs_db.db.remove_some_rows_from_table(t.hmm_hits_splits_table_name, where_clause=where_clause)

        self.progress.end()