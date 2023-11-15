        def push_record(record):
            for _spec in record.combined_depends:
                push_spec(_spec)
            if record.track_features:
                for ftr_name in record.track_features:
                    push_spec(MatchSpec(track_features=ftr_name))