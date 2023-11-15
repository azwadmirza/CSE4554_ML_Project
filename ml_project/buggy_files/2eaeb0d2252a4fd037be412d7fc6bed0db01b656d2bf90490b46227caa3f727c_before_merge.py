            def make_replacement(seg, policy):
                """Make a replacement segment, based on seen capitalisation."""
                if policy == "lower":
                    new_raw = seg.raw.lower()
                elif policy == "upper":
                    new_raw = seg.raw.upper()
                elif policy == "capitalize":
                    new_raw = seg.raw.capitalize()
                elif policy == "consistent":
                    if cases_seen:
                        # Get an element from what we've already seen
                        return make_replacement(seg, list(cases_seen)[0])
                    else:
                        # If we haven't seen anything yet, then let's default
                        # to upper
                        return make_replacement(seg, "upper")
                else:
                    raise ValueError("Unexpected capitalisation policy: {0!r}".format(policy))
                # Make a new class and return it.
                return seg.__class__(
                    raw=new_raw, pos_marker=seg.pos_marker
                )