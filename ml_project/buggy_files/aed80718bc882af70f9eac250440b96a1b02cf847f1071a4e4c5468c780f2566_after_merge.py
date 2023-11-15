def get_dependent_plate_dims(sites):
    """
    Return a list of dims for plates that are not common to all sites.
    """
    plate_sets = [site["cond_indep_stack"]
                  for site in sites if site["type"] == "sample"]
    all_plates = set().union(*plate_sets)
    common_plates = all_plates.intersection(*plate_sets)
    sum_plates = all_plates - common_plates
    sum_dims = list(sorted(f.dim for f in sum_plates if f.dim is not None))
    return sum_dims