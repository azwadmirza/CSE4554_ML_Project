    def store_genes_basic_info(self):
        if self.summary.quick:
            return

        self.progress.update('Sorting out gene calls ...')

        d = {}

        headers = ['contig', 'start', 'stop', 'direction']
        header_items_for_gene_sequences = ['dna_sequence']
        if self.summary.report_aa_seqs_for_gene_calls:
            header_items_for_gene_sequences.append('aa_sequence')

        for gene_callers_id in self.gene_caller_ids:
            d[gene_callers_id] = {}
            # add sample independent information into `d`;
            for header in headers:
                d[gene_callers_id][header] = self.summary.genes_in_contigs_dict[gene_callers_id][header]

            self.progress.update('Sorting out functions ...')
            # add functions if there are any:
            if len(self.summary.gene_function_call_sources):
                for source in self.summary.gene_function_call_sources:
                    if gene_callers_id not in self.summary.gene_function_calls_dict:
                        # this gene did not get any functional annotation
                        d[gene_callers_id][source] = ''
                        d[gene_callers_id][source + ' (ACCESSION)'] = ''
                        continue

                    if self.summary.gene_function_calls_dict[gene_callers_id][source]:
                        d[gene_callers_id][source + ' (ACCESSION)'] = self.summary.gene_function_calls_dict[gene_callers_id][source][0]
                        d[gene_callers_id][source] = self.summary.gene_function_calls_dict[gene_callers_id][source][1]
                    else:
                        d[gene_callers_id][source + ' (ACCESSION)'] = ''
                        d[gene_callers_id][source] = ''

            # finally add the dna and amino acid sequence for gene calls:
            contig = self.summary.genes_in_contigs_dict[gene_callers_id]['contig']
            start = self.summary.genes_in_contigs_dict[gene_callers_id]['start']
            stop = self.summary.genes_in_contigs_dict[gene_callers_id]['stop']

            dna_sequence = self.summary.contig_sequences[contig]['sequence'][start:stop]
            if self.summary.genes_in_contigs_dict[gene_callers_id]['direction'] == 'r':
                dna_sequence = utils.rev_comp(dna_sequence)

            d[gene_callers_id]['dna_sequence'] = dna_sequence

            # if the user asked for it, report amino acid sequences as well
            if self.summary.report_aa_seqs_for_gene_calls:
                try:
                    d[gene_callers_id]['aa_sequence'] = utils.get_translated_sequence_for_gene_call(dna_sequence, gene_callers_id)
                except:
                    d[gene_callers_id]['aa_sequence'] = ''

        output_file_obj = self.get_output_file_handle('gene_calls.txt')

        if self.summary.gene_function_call_sources:
            sources = [[source, source + ' (ACCESSION)'] for source in self.summary.gene_function_call_sources]
            headers = ['gene_callers_id'] + headers + [item for sublist in sources for item in sublist] + header_items_for_gene_sequences
        else:
            headers = ['gene_callers_id'] + headers + header_items_for_gene_sequences

        if self.summary.reformat_contig_names:
            for gene_callers_id in d:
                reformatted_contig_name = self.contig_name_conversion_dict[d[gene_callers_id]['contig']]['reformatted_contig_name']
                d[gene_callers_id]['contig'] = reformatted_contig_name

        self.progress.update('Storing genes basic info ...')
        utils.store_dict_as_TAB_delimited_file(d, None, headers=headers, file_obj=output_file_obj)

        self.bin_info_dict['genes'] = {'num_genes_found': len(self.gene_caller_ids)}