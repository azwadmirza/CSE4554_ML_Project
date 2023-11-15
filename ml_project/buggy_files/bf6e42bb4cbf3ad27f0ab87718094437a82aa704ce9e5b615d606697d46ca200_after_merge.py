    def handle_label(self, label, **options):
        plugin_pool.get_all_plugins()
        queryset = CMSPlugin.objects.filter(plugin_type=label)
        number_of_plugins = queryset.count()

        if number_of_plugins > 0:
            if options.get('interactive'):
                confirm = input("""
You have requested to remove %d '%s' plugins.
Are you sure you want to do this?
Type 'yes' to continue, or 'no' to cancel: """ % (number_of_plugins, label))
            else:
                confirm = 'yes'
            if confirm == 'yes':
                queryset.delete()
                self.stdout.write("%d '%s' plugins uninstalled\n" % (number_of_plugins, label))
            else:
                self.stdout.write('Aborted')
        else:
            self.stdout.write("no '%s' plugins found\n" % label)