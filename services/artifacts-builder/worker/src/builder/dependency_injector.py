import shutil
import os

def inject_plugin(build_dir, plugin_path):
    plugins_dir = os.path.join(build_dir, "plugins")
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
    shutil.copy(plugin_path, plugins_dir)
    return plugins_dir
