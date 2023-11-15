    def kaiju_stats_table(self):
        """ Take the parsed stats from the Kaiju reports and add them to the
        basic stats table at the top of the report """
        headers = {}
        general_data ={}
        taxo_ranks = self.kaiju_data.keys()

        # print only phylum rank in general table.
        if len(taxo_ranks) >= 1 and "phylum" in taxo_ranks:
            general_data = self.kaiju_data["phylum"]
            general_taxo_rank = "Phylum"
        else:
            general_data = self.kaiju_data[self.kaiju_data.keys().sorted()[0]]
            general_taxo_rank = self.kaiju_data.keys().sorted()[0].capitalize()

        headers['percentage_assigned'] = {
            'title': '% Reads assigned {}'.format(general_taxo_rank),
            'description': 'Percentage of reads assigned at {} rank'.format(general_taxo_rank),
            'min': 0,
            'max': 100,
            'suffix': '%',
            'scale': 'RdYlGn'
        }
        headers['assigned'] = {
            'title': '{} Reads assigned {} '.format(config.read_count_prefix, general_taxo_rank),
            'description': 'Number of reads assigned ({})  at {} rank'.format(config.read_count_desc, general_taxo_rank),
            'modify': lambda x: x * config.read_count_multiplier,
            'scale': 'Blues'
        }
        self.general_stats_addcols(general_data, headers)