def get_worksetcleaners():
    workset_funcs = []

    # copying functions is not implemented in IronPython 2.7.3
    if compat.IRONPY273:
        return workset_funcs

    # if model is workshared, get a list of current worksets
    if revit.doc.IsWorkshared:
        cl = DB.FilteredWorksetCollector(revit.doc)
        worksetlist = cl.OfKind(DB.WorksetKind.UserWorkset)
        # duplicate the workset element remover function for each workset
        for workset in worksetlist:
            workset_funcs.append(copy_func(template_workset_remover,
                                           workset.Name))

    return workset_funcs