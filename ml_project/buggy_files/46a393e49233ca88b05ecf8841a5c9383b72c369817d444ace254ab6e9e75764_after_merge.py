        def push_record(record):
            push_spec(MatchSpec(record.name))
            for _spec in record.combined_depends:
                push_spec(_spec)
            if record.track_features:
                for ftr_name in record.track_features:
                    push_spec(MatchSpec(track_features=ftr_name))