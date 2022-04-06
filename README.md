# blender-batch-bakery 🥐

blender add-on to bake entire hierarchies or multiple objects with one click. There are currently only two versions of the plugin. There is one version to bake Ambient Occlusion texture and export it embedded with the GLTF files (`AO-plugin.py`) and one to bake a 'combined' texture, connect it to the material output and export it as a GLTF file.

The plugin will create two folders in the same folder where the blend file is, one of them is called `bakes` and it contains all the textures while the other folder is called `baked_glb` and it contains the .glb files of the baked objects.
