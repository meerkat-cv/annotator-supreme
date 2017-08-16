import os
import importlib


class PluginsController():
    """
    A plugin must have the following interface:
        def process(image_matrix, image_object): -> process the image/annotations
            return (image_matrix, image_object)
        def init(dataset):            -> does the script initialization (possibly nothing)
        def end():             -> return json; does the script termination (possibly nothing)
        def get_parameters():  -> returns the script parameters. Not implemented yet.
            return {'parameters': []}
        def get_version():     -> get plugin version

    """
    def __init__(self):
        self.plugin = None
        self.plugin_obj = None

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


    def process(self, image_matrix, image_objec):
        return self.plugin_obj.process(image_matrix, image_objec)

    def init_plugin(self, dataset, partition = None):
        self.plugin_obj = self.plugin.AnnotatorPlugin(dataset, partition)
        
    def end_plugin(self):
        return self.plugin_obj.end()
