    def configure(self, options, updated):
        if "scripts" in updated:
            for s in options.scripts:
                if options.scripts.count(s) > 1:
                    raise exceptions.OptionsError("Duplicate script: %s" % s)

            for a in ctx.master.addons.chain[:]:
                if isinstance(a, Script) and a.name not in options.scripts:
                    ctx.log.info("Un-loading script: %s" % a.name)
                    ctx.master.addons.remove(a)

            # The machinations below are to ensure that:
            #   - Scripts remain in the same order
            #   - Scripts are listed directly after the script addon. This is
            #   needed to ensure that interactions with, for instance, flow
            #   serialization remains correct.
            #   - Scripts are not initialized un-necessarily. If only a
            #   script's order in the script list has changed, it should simply
            #   be moved.

            current = {}
            for a in ctx.master.addons.chain[:]:
                if isinstance(a, Script):
                    current[a.name] = a
                    ctx.master.addons.chain.remove(a)

            ordered = []
            newscripts = []
            for s in options.scripts:
                if s in current:
                    ordered.append(current[s])
                else:
                    ctx.log.info("Loading script: %s" % s)
                    sc = Script(s)
                    ordered.append(sc)
                    newscripts.append(sc)

            ochain = ctx.master.addons.chain
            pos = ochain.index(self)
            ctx.master.addons.chain = ochain[:pos + 1] + ordered + ochain[pos + 1:]

            for s in newscripts:
                ctx.master.addons.startup(s)