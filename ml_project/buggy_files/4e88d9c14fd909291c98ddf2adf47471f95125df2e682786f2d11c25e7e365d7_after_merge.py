    def get_enrichment_input(self, output_file_path):
        """This function converts modules mode output into input for anvi-script-enrichment-stats

        The input format for anvi-script-enrichment-stats is described in a comment at the top of that script, and here is
        how we get the values for each column:
        The first column, 'KEGG_MODULE', and second column 'accession', are already in the modules mode output as 'module_name'
        and 'kegg_module', respectively.
        The 'N_*' columns are the total number of samples in each group.
        For each module, this function determines which samples the module is 'present' in according to the specified completion threshold.
        This determines the list of samples for the 'sample_ids' column as well as the 'p_*' proportions for each group of samples.
        Finally, the fourth column, 'associated_groups', is computed from the 'p_*' proportions and 'N_*' totals.

        PARAMETERS
        ==========
        output_file_path : str
            a file path where we will store the (temporary) input file for the enrichment script
        """

        filesnpaths.is_output_file_writable(output_file_path)

        # read the files into dataframes
        modules_df = pd.read_csv(self.modules_txt, sep='\t')

        # make sure we have all the columns we need in modules mode output, since this output can be customized
        required_modules_txt_headers = ['kegg_module', 'module_completeness', 'module_name']
        missing_headers = []
        for h in required_modules_txt_headers:
            if h not in modules_df.columns:
                missing_headers.append(h)
        if missing_headers:
            missing_string = ", ".join(missing_headers)
            self.progress.reset()
            raise ConfigError("We cannot go on! *dramatic sweep*   We trust that you have provided us with "
                              "modules mode output, but unfortunately the modules-txt input does not contain "
                              f"the following required headers: {missing_string}   Please re-generate your "
                              "modules-txt to include these before trying again.")

        if 'unique_id' in modules_df.columns:
            modules_df = modules_df.drop(columns=['unique_id'])

        # samples column sanity check - this column will become the index
        if self.sample_header_in_modules_txt not in modules_df.columns:
            col_list = ", ".join(modules_df.columns)
            self.progress.reset()
            raise ConfigError(f"You have specified that your sample names are in the column with header '{self.sample_header_in_modules_txt}' "
                               "in the modules-txt file, but that column does not exist. :( Please figure out which column is right and submit "
                               "it using the --sample-header parameter. Just so you know, the columns in modules-txt that you can choose from "
                               f"are: {col_list}")

        required_groups_txt_headers = ['sample', 'group']
        sample_groups_dict = utils.get_TAB_delimited_file_as_dictionary(self.groups_txt, expected_fields=required_groups_txt_headers)
        samples_to_groups_dict = {samp : sample_groups_dict[samp]['group'] for samp in sample_groups_dict.keys()}

        # make sure the samples all have a group
        samples_with_none_group = []
        for s,g in samples_to_groups_dict.items():
            if not g:
                samples_with_none_group.append(s)
                if self.include_ungrouped:
                    samples_to_groups_dict[s] = 'UNGROUPED'

        if not self.include_ungrouped:
            for s in samples_with_none_group:
                samples_to_groups_dict.pop(s)

        if samples_with_none_group:
            self.progress.reset()
            none_group_str = ", ".join(samples_with_none_group)
            if self.include_ungrouped:
                self.run.warning("Some samples in your groups-txt did not have a group, but since you elected to --include-ungrouped, "
                                 "we will consider all of those samples to belong to one group called 'UNGROUPED'. Here are those "
                                 f"UNGROUPED samples: {none_group_str}")
            else:
                self.run.warning("Some samples in your groups-txt did not have a group, and we will ignore those samples. If you "
                                 "want them to be included in the analysis (but without assigning a group), you can simply re-run "
                                 "this program with the --include-ungrouped flag. Now. Here are the samples we will be ignoring: "
                                 f"{none_group_str}")

        # sanity check for mismatch between modules-txt and groups-txt
        sample_names_in_modules_txt = set(modules_df[self.sample_header_in_modules_txt].unique())
        sample_names_in_groups_txt = set(sample_groups_dict.keys())
        samples_missing_in_groups_txt = sample_names_in_modules_txt.difference(sample_names_in_groups_txt)
        samples_missing_in_modules_txt = sample_names_in_groups_txt.difference(sample_names_in_modules_txt)
        if anvio.DEBUG:
            self.run.info("Samples in modules-txt", ", ".join(list(sample_names_in_modules_txt)))
            self.run.info("Samples in groups-txt", ", ".join(list(sample_names_in_groups_txt)))
            self.run.info("Missing samples from groups-txt", ", ".join(list(samples_missing_in_groups_txt)))
            self.run.info("Missing samples from modules-txt", ", ".join(list(samples_missing_in_modules_txt)))

        if samples_missing_in_groups_txt:
            missing_samples_str = ", ".join(samples_missing_in_groups_txt)
            if not self.include_missing:
                self.progress.reset()
                self.run.warning(f"Your groups-txt file does not contain some samples present in your modules-txt ({self.sample_header_in_modules_txt} "
                                "column). Since you have not elected to --include-samples-missing-from-groups-txt, we are not going to take these samples into consideration at all. "
                                "Here are the samples that we will be ignoring: "
                                f"{missing_samples_str}")
                # drop the samples that are not in groups-txt
                modules_df = modules_df[~modules_df[self.sample_header_in_modules_txt].isin(list(samples_missing_in_groups_txt))]
                if anvio.DEBUG:
                    self.run.info("Samples remaining in modules-txt dataframe after removing ungrouped", ", ".join(modules_df[self.sample_header_in_modules_txt].unique()))

            else:
                self.progress.reset()
                self.run.warning(f"Your groups-txt file does not contain some samples present in your modules-txt ({self.sample_header_in_modules_txt} "
                                "column). Since you have chosen to --include-samples-missing-from-groups-txt, for the purposes of this analysis we will now consider all of "
                                "these samples to belong to one group called 'UNGROUPED'. If you wish to ignore these samples instead, please run again "
                                "without the --include-ungrouped parameter. "
                                "Here are the UNGROUPED samples that we will consider as one big happy family: "
                                f"{missing_samples_str}")
                # add those samples to the UNGROUPED group
                ungrouped_samples = list(samples_missing_in_groups_txt)
                for s in ungrouped_samples:
                    samples_to_groups_dict[s] = 'UNGROUPED'

        if samples_missing_in_modules_txt:
            missing_samples_str = ", ".join(samples_missing_in_modules_txt)
            if not self.just_do_it:
                self.progress.reset()
                raise ConfigError(f"Your modules-txt file ({self.sample_header_in_modules_txt} column) does not contain some samples that "
                                 "are present in your groups-txt. This is not necessarily a huge deal, it's just that those samples will "
                                 "not be included in the enrichment analysis because, well, you don't have any module information for them. "
                                 "If all of the missing samples belong to groups you don't care about at all, then feel free to ignore this "
                                 "message and re-run using --just-do-it. But if you do care about those groups, you'd better fix this because "
                                 "the enrichment results for those groups will be wrong. Here are the samples in question: "
                                  f"{missing_samples_str}")
            else:
                self.progress.reset()
                self.run.warning(f"Your modules-txt file ({self.sample_header_in_modules_txt} column) does not contain some samples that "
                                 "are present in your groups-txt. This is not necessarily a huge deal, it's just that those samples will "
                                 "not be included in the enrichment analysis because, well, you don't have any module information for them. "
                                 "Since you have used the --just-do-it parameter, we assume you don't care about this and are going to keep "
                                 "going anyway. We hope you know what you are doing :) Here are the samples in question: "
                                  f"{missing_samples_str}")
                # drop the samples that are not in modules-txt
                for s in list(samples_missing_in_modules_txt):
                    samples_to_groups_dict.pop(s)
                if anvio.DEBUG:
                    self.run.info("Samples remaining in groups-txt dataframe after removing ungrouped", ", ".join(samples_to_groups_dict.keys()))


        modules_df.set_index(self.sample_header_in_modules_txt, inplace=True)
        sample_groups_df = pd.DataFrame.from_dict(samples_to_groups_dict, orient="index", columns=['group'])

        # convert modules mode output to enrichment input
        N_values = sample_groups_df['group'].value_counts()
        group_list = N_values.keys()
        module_list = modules_df['kegg_module'].unique()

        output_dict = {}
        header_list = ['KEGG_MODULE', 'accession', 'sample_ids', 'associated_groups']
        for c in group_list:
            header_list.append(f"p_{c}")
            header_list.append(f"N_{c}")

        for mod_num in module_list:
            query_string = f"kegg_module == '{mod_num}' and module_completeness >= {self.module_completion_threshold}"
            samples_with_mod_df = modules_df.query(query_string)
            if samples_with_mod_df.shape[0] == 0:
                continue
            # if we are working with module data from metagenomes, we may have multiple complete copies of the module in
            # the same sample. We drop these duplicates before proceeding.
            duplicates = samples_with_mod_df.index.duplicated()
            samples_with_mod_df = samples_with_mod_df[~duplicates]
            
            mod_name = samples_with_mod_df['module_name'][0]
            output_dict[mod_name] = {}
            output_dict[mod_name]['KEGG_MODULE'] = mod_name
            output_dict[mod_name]['accession'] = mod_num
            samples_with_mod_list = list(samples_with_mod_df.index)
            output_dict[mod_name]['sample_ids'] = ','.join(samples_with_mod_list)
            sample_group_subset = sample_groups_df.loc[samples_with_mod_list]
            p_values = sample_group_subset['group'].value_counts()

            # we need the categories p and N values to be in the same order for finding associated groups
            p_vector = np.array([])
            N_vector = np.array([])
            for c in group_list:
                if c not in p_values.index:
                    p_values[c] = 0
                p_vector = np.append(p_vector, p_values[c]/N_values[c])
                N_vector = np.append(N_vector, N_values[c])

            # compute associated groups for functional enrichment
            enriched_groups_vector = utils.get_enriched_groups(p_vector, N_vector)

            associated_groups = [c for i,c in enumerate(group_list) if enriched_groups_vector[i]]
            output_dict[mod_name]['associated_groups'] = ','.join(associated_groups)

            for c in group_list:
                output_dict[mod_name]["p_%s" % c] = p_values[c]/N_values[c]
                output_dict[mod_name]["N_%s" % c] = N_values[c]

        utils.store_dict_as_TAB_delimited_file(output_dict, output_file_path, key_header='accession', headers=header_list)