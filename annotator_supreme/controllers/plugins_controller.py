import os
import importlib


class PluginsController():
    """
    A plugin must have the following interface:
        def process(im, anno, dataset_name): -> process the image/annotations
            return (im, anno, res)
                where res is a dictionary serialziable (json)
        def init():            -> does the script initialization (possibly nothing)
        def end():             -> does the script termination (possibly nothing)
        def get_parameters():  -> returns the script parameters. Not implemented yet.
            return {'parameters': []}
        def get_version():     -> get plugin version

    """
    def __init__(self):
        self.plugin = None

    def get_all_plugins(self):
        plugins = os.listdir('./annotator_supreme/plugins/')
        list_plugins = []
        for p in plugins:
            if os.path.splitext(p)[1].lower() != '.py':
                continue
            plugin_name = os.path.splitext(p)[0].replace('_',' ').title()
            list_plugins.append(plugin_name)

        return list_plugins

    def load_plugin(self, plugin_name):
        try:
            plugin_name = plugin_name.lower().replace(' ','_')
            plugin_name = 'annotator_supreme.plugins.' + plugin_name
            self.plugin = __import__(plugin_name, globals(), locals(), ['object'])
            importlib.reload(self.plugin) # make sure it is the latest version
        except BaseException as e:
            print(str(e))
            return False

        return True


    def process(self, im, anno):
        return self.plugin.process(im, anno)

    def init_plugin(self):
        self.plugin.init()

    def end_plugin(self):
        self.plugin.end()
