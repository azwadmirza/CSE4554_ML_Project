    def iter_by_area(self):
        """Generate datasets grouped by Area.

        :return: generator of (area_obj, list of dataset objects)
        """
        datasets_by_area = {}
        for ds in self:
            a = ds.info.get('area')
            a_str = str(a) if a is not None else None
            datasets_by_area.setdefault(
                a_str, (a, []))
            datasets_by_area[a_str][1].append(ds.id)

        for area_name, (area_obj, ds_list) in datasets_by_area.items():
            yield area_obj, ds_list