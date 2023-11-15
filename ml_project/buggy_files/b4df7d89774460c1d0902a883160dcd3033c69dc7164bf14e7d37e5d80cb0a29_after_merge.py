def get_worksetcleaners():
    workset_funcs = []
    # if model is workshared, get a list of current worksets
    if revit.doc.IsWorkshared:
        cl = DB.FilteredWorksetCollector(revit.doc)
        worksetlist = cl.OfKind(DB.WorksetKind.UserWorkset)
        # duplicate the workset element remover function for each workset
        for workset in worksetlist:
            # copying functions is not implemented in IronPython 2.7.3
            # this method initially used copy_func to create a func for
            # each workset but now passes on the template func
            # with appropriate arguments
            docstr = WORKSET_FUNC_DOCSTRING_TEMPLATE.format(workset.Name)
            workset_funcs.append(
                WorksetFuncData(
                    func=template_workset_remover,
                    docstring=docstr,
                    args=(workset.Name,)
                    )
                )

    return workset_funcs