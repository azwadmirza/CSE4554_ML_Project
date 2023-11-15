    def send_report(self):
        if not self.data:
            self.report_paragraph("No data.")
            return

        pdesc = None
        describe_domain = False
        for d in (self.data_desc, self.match_desc, self.nonmatch_desc):
            if not d or not d["Data instances"]:
                continue
            ndesc = d.copy()
            del ndesc["Data instances"]
            if pdesc is not None and pdesc != ndesc:
                describe_domain = True
            pdesc = ndesc

        conditions = []
        domain = self.data.domain
        for attr_name, oper, values in self.conditions:
            if attr_name in self.AllTypes:
                attr = attr_name
                names = self.operator_names[attr_name]
                var_type = self.AllTypes[attr_name]
            else:
                attr = domain[attr_name]
                var_type = vartype(attr)
                names = self.operator_names[type(attr)]
            name = names[oper]
            if oper == len(names) - 1:
                conditions.append("{} {}".format(attr, name))
            elif var_type == 1:  # discrete
                if name == "is one of":
                    valnames = [attr.values[v - 1] for v in values]
                    if not valnames:
                        continue
                    if len(valnames) == 1:
                        valstr = valnames[0]
                    else:
                        valstr = f"{', '.join(valnames[:-1])} or {valnames[-1]}"
                    conditions.append(f"{attr} is {valstr}")
                elif values and values[0]:
                    value = values[0] - 1
                    conditions.append(f"{attr} {name} {attr.values[value]}")
            elif var_type == 3:  # string variable
                conditions.append(
                    f"{attr} {name} {' and '.join(map(repr, values))}")
            elif all(x for x in values):  # numeric variable
                conditions.append(f"{attr} {name} {' and '.join(values)}")
        items = OrderedDict()
        if describe_domain:
            items.update(self.data_desc)
        else:
            items["Instances"] = self.data_desc["Data instances"]
        items["Condition"] = " AND ".join(conditions) or "no conditions"
        self.report_items("Data", items)
        if describe_domain:
            self.report_items("Matching data", self.match_desc)
            self.report_items("Non-matching data", self.nonmatch_desc)
        else:
            match_inst = \
                bool(self.match_desc) and \
                self.match_desc["Data instances"]
            nonmatch_inst = \
                bool(self.nonmatch_desc) and \
                self.nonmatch_desc["Data instances"]
            self.report_items(
                "Output",
                (("Matching data",
                  "{} instances".format(match_inst) if match_inst else "None"),
                 ("Non-matching data",
                  nonmatch_inst > 0 and "{} instances".format(nonmatch_inst))))