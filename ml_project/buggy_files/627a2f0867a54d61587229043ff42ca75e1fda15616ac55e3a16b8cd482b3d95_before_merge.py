def delete_linked_data(prefix, dist, delete=True):
    recs = linked_data_.get(prefix)
    if recs and dist in recs:
        del recs[dist]
    if delete:
        meta_path = join(prefix, 'conda-meta', _dist2filename(dist, '.json'))
        if isfile(meta_path):
            os.unlink(meta_path)