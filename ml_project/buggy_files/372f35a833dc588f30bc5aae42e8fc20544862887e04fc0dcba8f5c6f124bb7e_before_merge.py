    def fix_string(self, verbosity=0):
        """Obtain the changes to a path as a string.

        We use the file_mask to do a safe merge, avoiding any templated
        sections. First we need to detect where there have been changes
        between the fixed and templated versions.

        We use difflib.SequenceMatcher.get_opcodes
        See: https://docs.python.org/3.7/library/difflib.html#difflib.SequenceMatcher.get_opcodes
        It returns a list of tuples ('equal|replace', ia1, ia2, ib1, ib2).

        """
        verbosity_logger("Persisting file masks: {0}".format(self.file_mask), verbosity=verbosity)
        # Compare Templated with Raw
        diff_templ = SequenceMatcher(autojunk=None, a=self.file_mask[0], b=self.file_mask[1])
        diff_templ_codes = diff_templ.get_opcodes()
        verbosity_logger("Templater diff codes: {0}".format(diff_templ_codes), verbosity=verbosity)

        # Compare Fixed with Templated
        diff_fix = SequenceMatcher(autojunk=None, a=self.file_mask[1], b=self.file_mask[2])
        # diff_fix = SequenceMatcher(autojunk=None, a=self.file_mask[1][0], b=self.file_mask[2][0])
        diff_fix_codes = diff_fix.get_opcodes()
        verbosity_logger("Fixing diff codes: {0}".format(diff_fix_codes), verbosity=verbosity)

        # If diff_templ isn't the same then we should just keep the template. If there *was*
        # a fix in that space, then we should raise an issue
        # If it is the same, then we can apply fixes as expected.
        write_buff = ''
        fixed_block = None
        templ_block = None
        # index in raw, templ and fix
        idx = (0, 0, 0)
        loop_idx = 0
        while True:
            loop_idx += 1
            verbosity_logger(
                "{0:04d}: Write Loop: idx:{1}, buff:{2!r}".format(loop_idx, idx, write_buff),
                verbosity=verbosity)

            if templ_block is None:
                if diff_templ_codes:
                    templ_block = diff_templ_codes.pop(0)
                # We've exhausted the template. Have we exhausted the fixes?
                elif fixed_block is None:
                    # Yes - excellent. DONE
                    break
                else:
                    raise NotImplementedError("Fix Block left over! DOn't know how to handle this! aeflf8wh")
            if fixed_block is None:
                if diff_fix_codes:
                    fixed_block = diff_fix_codes.pop(0)
                else:
                    raise NotImplementedError("Unexpectedly depleted the fixes. Panic!")
            verbosity_logger(
                "{0:04d}: Blocks: template:{1}, fix:{2}".format(loop_idx, templ_block, fixed_block),
                verbosity=verbosity)

            if templ_block[0] == 'equal':
                if fixed_block[0] == 'equal':
                    # No templating, no fixes, go with middle and advance indexes
                    # Find out how far we can advance (we use the middle version because it's common)
                    if templ_block[4] == fixed_block[2]:
                        buff = self.file_mask[1][idx[1]:fixed_block[2]]
                        # consume both blocks
                        fixed_block = None
                        templ_block = None
                    elif templ_block[4] > fixed_block[2]:
                        buff = self.file_mask[1][idx[1]:fixed_block[2]]
                        # consume fixed block
                        fixed_block = None
                    elif templ_block[4] < fixed_block[2]:
                        buff = self.file_mask[1][idx[1]:templ_block[4]]
                        # consume templ block
                        templ_block = None
                    idx = (idx[0] + len(buff), idx[1] + len(buff), idx[2] + len(buff))
                    write_buff += buff
                    continue
                elif fixed_block[0] == 'replace':
                    # Consider how to apply fixes.
                    # Can we implement the fix while staying in the equal segment?
                    if fixed_block[2] <= templ_block[4]:
                        # Yes! Write from the fixed version.
                        write_buff += self.file_mask[2][idx[2]:fixed_block[4]]
                        idx = (idx[0] + (fixed_block[2] - fixed_block[1]), fixed_block[2], fixed_block[4])
                        # Consume the fixed block because we've written the whole thing.
                        fixed_block = None
                        continue
                    else:
                        raise NotImplementedError("DEF")
                elif fixed_block[0] == 'delete':
                    # We're deleting items, nothing to write but we can consume some
                    # blocks and advance some indexes.
                    idx = (idx[0] + (fixed_block[2] - fixed_block[1]), fixed_block[2], fixed_block[4])
                    fixed_block = None
                elif fixed_block[0] == 'insert':
                    # We're inserting items, Write from the fix block, but only that index moves.
                    write_buff += self.file_mask[2][idx[2]:fixed_block[4]]
                    idx = (idx[0], idx[1], fixed_block[4])
                    fixed_block = None
                else:
                    raise ValueError(
                        ("Unexpected opcode {0} for fix block! Please report this "
                         "issue on github with the query and rules you're trying to "
                         "fix.").format(fixed_block[0]))
            elif templ_block[0] == 'replace':
                # We're in a templated section - we should write the templated version.
                # we should consume the whole replce block and then deal with where
                # we end up.
                buff = self.file_mask[0][idx[0]:templ_block[2]]
                new_templ_idx = templ_block[4]
                while True:
                    if fixed_block[2] > new_templ_idx >= fixed_block[1]:
                        # this block contains the end point
                        break
                    else:
                        if fixed_block[0] != 'equal':
                            print("WARNING: Skipping edit block: {0}".format(fixed_block))
                        fixed_block = None
                # Are we exaclty on a join?
                if new_templ_idx == fixed_block[1]:
                    # GREAT - this makes things easy because we have an equality point already
                    idx = (templ_block[2], new_templ_idx, fixed_block[3])
                else:
                    if fixed_block[0] == 'equal':
                        # If it's in an equal block, we can use the same offset from the end.
                        idx = (templ_block[2], new_templ_idx, fixed_block[3] + (new_templ_idx - fixed_block[1]))
                    else:
                        # TODO: We're trying to move through an templated section, but end up
                        # in a fixed section. We've lost track of indexes.
                        # We might need to panic if this happens...
                        print("UMMMMMM!")
                        print(new_templ_idx)
                        print(fixed_block)
                        raise NotImplementedError("ABC")
                write_buff += buff
                # consume template block
                templ_block = None
            elif templ_block[0] == 'delete':
                # The comparison, things that the templater has deleted
                # some characters. This is just a quirk of the differ.
                # In reality this means we just write these characters
                # and don't worry about advancing the other indexes.
                buff = self.file_mask[0][idx[0]:templ_block[2]]
                # consume templ block
                templ_block = None
                idx = (idx[0] + len(buff), idx[1], idx[2])
                write_buff += buff
            else:
                raise ValueError(
                    ("Unexpected opcode {0} for template block! Please report this "
                     "issue on github with the query and rules you're trying to "
                     "fix.").format(templ_block[0]))

        return write_buff