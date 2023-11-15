    def peddy_sex_check_plot(self):
        data = {}
        sex_index = {"female": 0, "male": 1, "unknown": 2}

        for s_name, d in self.peddy_data.items():
            if 'sex_het_ratio' in d and 'ped_sex_sex_check' in d:
                data[s_name] = {
                    'x': sex_index.get(d['ped_sex_sex_check'], 2),
                    'y': d["sex_het_ratio"]
                }

        pconfig = {
            'id': 'peddy_sex_check_plot',
            'title': 'Peddy: Sex Check',
            'xlab': 'Sex From Ped',
            'ylab': 'Sex Het Ratio',
            'categories': ["Female", "Male", "Unknown"]
        }

        if len(data) > 0:
            self.add_section(
                name = 'Sex Check',
                description = "Predicted sex against heterozygosity ratio",
                helptext = """
                Higher values of Sex Het Ratio suggests the sample is female, low values suggest male.

                See [the main peddy documentation](http://peddy.readthedocs.io/en/latest/#sex-check) for more details about the `het_check` command.
                """,
                anchor='peddy-sexcheck-plot',
                plot=scatter.plot(data, pconfig)
            )