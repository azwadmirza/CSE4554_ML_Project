    def visit_Template(self, node, frame=None):
        assert frame is None, 'no root frame allowed'
        eval_ctx = EvalContext(self.environment, self.name)

        from jinja2.runtime import __all__ as exported
        self.writeline('from __future__ import %s' % ', '.join(code_features))
        self.writeline('from jinja2.runtime import ' + ', '.join(exported))

        if self.environment.is_async:
            self.writeline('from jinja2.asyncsupport import auto_await, '
                           'auto_aiter, make_async_loop_context')

        # if we want a deferred initialization we cannot move the
        # environment into a local name
        envenv = not self.defer_init and ', environment=environment' or ''

        # do we have an extends tag at all?  If not, we can save some
        # overhead by just not processing any inheritance code.
        have_extends = node.find(nodes.Extends) is not None

        # find all blocks
        for block in node.find_all(nodes.Block):
            if block.name in self.blocks:
                self.fail('block %r defined twice' % block.name, block.lineno)
            self.blocks[block.name] = block

        # find all imports and import them
        for import_ in node.find_all(nodes.ImportedName):
            if import_.importname not in self.import_aliases:
                imp = import_.importname
                self.import_aliases[imp] = alias = self.temporary_identifier()
                if '.' in imp:
                    module, obj = imp.rsplit('.', 1)
                    self.writeline('from %s import %s as %s' %
                                   (module, obj, alias))
                else:
                    self.writeline('import %s as %s' % (imp, alias))

        # add the load name
        self.writeline('name = %r' % self.name)

        # generate the root render function.
        self.writeline('%s(context, missing=missing%s):' %
                       (self.func('root'), envenv), extra=1)
        self.indent()
        self.write_commons()

        # process the root
        frame = Frame(eval_ctx)
        if 'self' in find_undeclared(node.body, ('self',)):
            ref = frame.symbols.declare_parameter('self')
            self.writeline('%s = TemplateReference(context)' % ref)
        frame.symbols.analyze_node(node)
        frame.toplevel = frame.rootlevel = True
        frame.require_output_check = have_extends and not self.has_known_extends
        if have_extends:
            self.writeline('parent_template = None')
        self.enter_frame(frame)
        self.pull_dependencies(node.body)
        self.blockvisit(node.body, frame)
        self.leave_frame(frame, with_python_scope=True)
        self.outdent()

        # make sure that the parent root is called.
        if have_extends:
            if not self.has_known_extends:
                self.indent()
                self.writeline('if parent_template is not None:')
            self.indent()
            if supports_yield_from:
                self.writeline('yield from parent_template.'
                               'root_render_func(context)')
            else:
                self.writeline('for event in parent_template.'
                               'root_render_func(context):')
                self.indent()
                self.writeline('yield event')
                self.outdent()
            self.outdent(1 + (not self.has_known_extends))

        # at this point we now have the blocks collected and can visit them too.
        for name, block in iteritems(self.blocks):
            self.writeline('%s(context, missing=missing%s):' %
                           (self.func('block_' + name), envenv),
                           block, 1)
            self.indent()
            self.write_commons()
            # It's important that we do not make this frame a child of the
            # toplevel template.  This would cause a variety of
            # interesting issues with identifier tracking.
            block_frame = Frame(eval_ctx)
            undeclared = find_undeclared(block.body, ('self', 'super'))
            if 'self' in undeclared:
                ref = block_frame.symbols.declare_parameter('self')
                self.writeline('%s = TemplateReference(context)' % ref)
            if 'super' in undeclared:
                ref = block_frame.symbols.declare_parameter('super')
                self.writeline('%s = context.super(%r, '
                               'block_%s)' % (ref, name, name))
            block_frame.symbols.analyze_node(block)
            block_frame.block = name
            self.enter_frame(block_frame)
            self.pull_dependencies(block.body)
            self.blockvisit(block.body, block_frame)
            self.leave_frame(block_frame, with_python_scope=True)
            self.outdent()

        self.writeline('blocks = {%s}' % ', '.join('%r: block_%s' % (x, x)
                                                   for x in self.blocks),
                       extra=1)

        # add a function that returns the debug info
        self.writeline('debug_info = %r' % '&'.join('%s=%s' % x for x
                                                    in self.debug_info))