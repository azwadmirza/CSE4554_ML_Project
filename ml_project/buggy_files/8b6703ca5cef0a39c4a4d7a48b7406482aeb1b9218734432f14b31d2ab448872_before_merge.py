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
            attr_index = domain.index(attr_name)
            attr = domain[attr_index]
            names = self.operator_names[type(attr)]
            name = names[oper]
            if oper == len(names) - 1:
                conditions.append("{} {}".format(attr, name))
            elif attr.is_discrete:
                if name == "is one of":
                    if len(values) == 1:
                        conditions.append("{} is {}".format(
                            attr, attr.values[values[0] - 1]))
                    elif len(values) > 1:
                        conditions.append("{} is {} or {}".format(
                            attr,
                            ", ".join(attr.values[v - 1] for v in values[:-1]),
                            attr.values[values[-1] - 1]))
                else:
                    if not (values and values[0]):
                        continue
                    value = values[0] - 1
                    conditions.append("{} {} {}".
                                      format(attr, name, attr.values[value]))
            else:
                if len(values) == 1:
                    conditions.append("{} {} {}".
                                      format(attr, name, *values))
                else:
                    conditions.append("{} {} {} and {}".
                                      format(attr, name, *values))
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