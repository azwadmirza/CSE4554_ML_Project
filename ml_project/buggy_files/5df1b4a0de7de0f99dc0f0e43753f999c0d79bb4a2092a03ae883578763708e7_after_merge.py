    def store_hits_into_contigs_db(self):
        if not self.hits:
            raise ConfigError("COGs class has no hits to process. Did you forget to call search?")

        cogs_data = COGsData(self.args)
        cogs_data.init_p_id_to_cog_id_dict()

        functions_dict = {}
        self.__entry_id = 0


        def add_entry(gene_callers_id, source, accession, function, e_value):
            functions_dict[self.__entry_id] = {'gene_callers_id': int(gene_callers_id),
                                        'source': source,
                                        'accession': accession,
                                        'function': function,
                                        'e_value': float(e_value)}
            self.__entry_id += 1

        # let's keep track of hits that match to missing COGs
        hits_for_missing_cogs = 0
        missing_cogs_found = set([])

        for gene_callers_id in self.hits:
            ncbi_protein_id = self.hits[gene_callers_id]['hit']

            in_proteins_FASTA_not_in_cogs_CSV = []
            if ncbi_protein_id not in cogs_data.p_id_to_cog_id:
                in_proteins_FASTA_not_in_cogs_CSV.append((ncbi_protein_id, gene_callers_id),)
            else:
                COG_ids = cogs_data.p_id_to_cog_id[ncbi_protein_id]

            annotations = []
            categories = set([])
            for COG_id in COG_ids:
                # is missing?
                if COG_id in cogs_data.missing_cogs:
                    missing_cogs_found.add(COG_id)
                    hits_for_missing_cogs += 1
                    continue

                # resolve categories
                for category in cogs_data.cogs[COG_id]['categories']:
                    categories.add(category)

                # append annotation
                annotations.append(cogs_data.cogs[COG_id]['annotation'])

            # all these shitty heuristics... If there are multiple COG ids or categories, separate them from each other by '!!!' so parsing
            # them later is possible. Am I embarrassed? Yes. Is there a better way of doing this efficiently? Absolutely. What time is it?
            # 9pm. Where am I? In the lab. Is it OK for me to let this slip away if it means for me to go home sooner? Yes, probably. Am I
            # gonna remember this crap in the code for the next two months at random times in the shower and feel bad about myself? Fuck yes.
            add_entry(gene_callers_id, 'COG_FUNCTION', '!!!'.join(COG_ids), '!!!'.join(annotations), self.hits[gene_callers_id]['evalue'])
            add_entry(gene_callers_id, 'COG_CATEGORY', '!!!'.join(categories), '!!!'.join(categories), 0.0)

        # store hits in contigs db.
        gene_function_calls_table = dbops.TableForGeneFunctions(self.contigs_db_path, self.run, self.progress)
        gene_function_calls_table.create(functions_dict)

        if len(missing_cogs_found):
            self.run.warning('Although your COGs are successfully added to the database, there were some COG IDs your genes hit\
                              were among the ones that were not described in the raw data. Here is the list of %d COG IDs that\
                              were hit %d times: %s.' % (len(missing_cogs_found), hits_for_missing_cogs, ', '.join(missing_cogs_found)))

        if len(in_proteins_FASTA_not_in_cogs_CSV):
            # so some of the hits represented in the FASTA file from the NCBI were not put in the
            # CSV file from NCBI to associate them with COGs
            report_output_file_path = filesnpaths.get_temp_file_path()
            report_output = open(report_output_file_path, 'w')
            report_output.write('anvio_gene_callers_id\tNCBI_protein_id\n')

            for protein_id, gene_callers_id in in_proteins_FASTA_not_in_cogs_CSV:
                report_output.write('%s\t%s\n' % (gene_callers_id, protein_id))

            report_output.close()

            self.run.warning("This is important. %s hits for your genes that appeared in the proteins FASTA file from the NCBI had protein\
                              IDs that were not described in the CSV file from the NCBI that associates each protein ID with a COG function.\
                              That's OK if you don't care. But if you would like to take a look, anvi'o stored a report\
                              file for you at %s" \
                        % (len(in_proteins_FASTA_not_in_cogs_CSV), report_output_file_path))