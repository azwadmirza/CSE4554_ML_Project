    def store_sequences_for_hmm_hits(self):
        if self.summary.quick:
            return

        s = SequencesForHMMHits(self.summary.contigs_db_path, split_names_of_interest=self.split_names, progress=progress_quiet, bin_name=self.bin_id)
        hmm_sequences_dict = s.get_sequences_dict_for_hmm_hits_in_splits({self.bin_id: self.split_names})

        if self.summary.reformat_contig_names:
            for entry_id in hmm_sequences_dict:
                reformatted_contig_name = self.contig_name_conversion_dict[hmm_sequences_dict[entry_id]['contig']]['reformatted_contig_name']
                hmm_sequences_dict[entry_id]['contig'] = reformatted_contig_name

        single_copy_gene_hmm_sources = [hmm_search_source for hmm_search_type, hmm_search_source in self.summary.hmm_searches_header]
        non_single_copy_gene_hmm_sources = self.summary.completeness.sources

        for hmm_search_source in single_copy_gene_hmm_sources + non_single_copy_gene_hmm_sources:
            filtered_hmm_sequences_dict = utils.get_filtered_dict(hmm_sequences_dict, 'source', set([hmm_search_source]))

            output_file_obj = self.get_output_file_handle('%s-hmm-sequences.txt' % hmm_search_source, key=hmm_search_source)

            for gene_unique_id in filtered_hmm_sequences_dict:
                header, sequence = s.get_FASTA_header_and_sequence_for_gene_unique_id(hmm_sequences_dict, gene_unique_id)
                output_file_obj.write('>%s\n%s\n' % (header, sequence))