import bpy
from datetime import datetime
import os

def bake_texture(obj, width, height, bake_type, img_format):
    print("OBJECT BAKING: ", obj.name)
    now = datetime.now()
    image_name = obj.name + '_bake'
    img = bpy.data.images.new(image_name,width,height)
    
    for mat in obj.data.materials:
        for n in mat.node_tree.nodes:
            if n.name == 'Bake_node':
                mat.node_tree.nodes.remove(n)

    for ma in obj.data.materials:
        mat = ma.copy()
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        texture_node =nodes.new('ShaderNodeTexImage')
        texture_node.name = 'Bake_node'
        texture_node.select = True
        nodes.active = texture_node
        texture_node.image = img
        

    bpy.context.view_layer.objects.active = obj
    obj.active_material = mat
    bpy.ops.object.bake(type=bake_type,save_mode='EXTERNAL')
        
    path = os.path.join(bpy.path.abspath("//"), 'bakes')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, image_name+img_format)

    img.save_render(filepath=path)

    for mat in obj.data.materials:
        for n in mat.node_tree.nodes:
            if n.name == 'Bake_node':
                output = mat.node_tree.nodes.get('Material Output')
                mat.node_tree.links.new(n.outputs[0], output.inputs[0])
                
    print("BAKED. TIME TAKEN: ", datetime.now() - now)


def recursive_baking(object, width, height, bake_type, img_format):
    bpy.ops.object.select_all(action='DESELECT')
    if object.type == "MESH" and len(object.children) == 0 and len(object.data.materials.items()) > 0:
        object.select_set(True)
        bake_texture(object, width, height, bake_type, img_format)
    for obj in object.children:
        if len(obj.children) > 0:
            recursive_baking(obj, width, height, bake_type, img_format)
        if obj.type == "MESH" and len(obj.data.materials.items()) > 0:
            obj.select_set(True)
            bake_texture(obj, width, height, bake_type, img_format)

        
def recursive_connecting(object, img_format):
    bpy.ops.object.select_all(action='DESELECT')
    if object.type == "MESH" and len(object.children) == 0 and len(object.data.materials.items()) > 0:
        object.select_set(True)
        connect(object, img_format)
    for obj in object.children:
        if len(obj.children) > 0:
            recursive_connecting(obj, img_format)
        if obj.type == "MESH" and len(obj.data.materials.items()) > 0:
            obj.select_set(True)
            connect(obj, img_format)

def connect(obj, img_format):
    print("CONNECTED: ", obj.name)
    for mat in obj.data.materials:
        for n in mat.node_tree.nodes:
            if n.name == 'Bake_node':
                output = mat.node_tree.nodes.get('Material Output')
                
                image_name = obj.name + '_bake'
                path = os.path.join(bpy.path.abspath("//"), 'bakes')
                if not os.path.exists(path):
                    os.makedirs(path)
                path = os.path.join(path, image_name+img_format)

                img = bpy.data.images.load(path, check_existing=True)
                n.image = img
                
                mat.node_tree.links.new(n.outputs[0], output.inputs[0])
                
def select_hierarchy(object):
    object.select_set(True)
    for obj in object.children:
        select_hierarchy(obj)


#obj = bpy.context.active_object
#recursive_baking(obj)
#recursive_connecting(obj)
#bpy.ops.object.select_all(action='DESELECT')
#select_hierarchy(obj)
#bpy.ops.export_scene.gltf(filepath='//baked_glbs/'+obj.name+'.glb', export_format='GLB', use_selection=True)






bl_info = {
    "name": "Baking Plug-in",
    "description": "Bake entire hierarchies of objects all in one click",
    "author": "elia",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}


import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):

#    my_bool: BoolProperty(
#        name="Enable or Disable",
#        description="A bool property",
#        default = False
#        )

#    my_int: IntProperty(
#        name = "Int Value",
#        description="A integer property",
#        default = 23,
#        min = 10,
#        max = 100
#        )
    texture_width: IntProperty(
        name = "Width",
        description="width of the texture",
        default = 2048,
        min = 8,
        max = 10000
        )
    texture_height: IntProperty(
        name = "Height",
        description="height of the texture",
        default = 2048,
        min = 8,
        max = 10000
        )

#    my_float: FloatProperty(
#        name = "Float Value",
#        description = "A float property",
#        default = 23.7,
#        min = 0.01,
#        max = 30.0
#        )

#    my_float_vector: FloatVectorProperty(
#        name = "Float Vector Value",
#        description="Something",
#        default=(0.0, 0.0, 0.0), 
#        min= 0.0, # float
#        max = 0.1
#    ) 

#    my_path: StringProperty(
#        name = "Directory",
#        description="Choose a directory:",
#        default="",
#        maxlen=1024,
#        subtype='DIR_PATH'
#        )
#        
    bake_type: EnumProperty(
        name="",
        description="bake type",
        items=[ ('COMBINED', "Combined", ""),
                ('DIFFUSE', "Diffuse", ""),
                ('AO', "Ambient Occlusion", ""),
                ('GLOSSY', "Glossy", ""),
                ('ROUGHNESS', "Roughness", ""),
                ('SHADOW', "Shadow", "")
               ]
        )

    img_format: EnumProperty(
        name="",
        description="file extension of texture images",
        items=[ ('.png', "PNG", ""),
                ('.jpg', "JPG", "")
               ]
        )

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_HelloWorld(Operator):
    bl_label = "Bake"
    bl_idname = "wm.hello_world"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

#        print("bool state:", mytool.my_bool)
#        print("int value:", mytool.my_int)
#        print("float value:", mytool.my_float)
#        print("string value:", mytool.my_string)
#        print("enum state:", mytool.my_enum)

        self.report({'INFO'}, "Started Baking")
        
        texture_width = mytool.texture_width
        texture_height = mytool.texture_height
        bake_type = mytool.bake_type
        img_format = mytool.img_format

        obj = bpy.context.active_object
        recursive_baking(obj, texture_width, texture_height, bake_type, img_format)
        recursive_connecting(obj, img_format)
        bpy.ops.object.select_all(action='DESELECT')
        select_hierarchy(obj)
        
        path = os.path.join(bpy.path.abspath("//"), 'baked_glbs')
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, obj.name+'.glb')
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True)
        
        self.report({'INFO'}, "Finished Baking")

        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Menus
# ------------------------------------------------------------------------

class OBJECT_MT_CustomMenu(bpy.types.Menu):
    bl_label = "Select"
    bl_idname = "OBJECT_MT_custom_menu"

    def draw(self, context):
        layout = self.layout

        # Built-in operators
        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")

# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "HoR baking plugin"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Baking Plugin"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        layout.label(text="TEXTURE SIZES")

#        layout.prop(mytool, "my_bool")
#        layout.prop(mytool, "my_enum", text="") 
#        layout.prop(mytool, "my_int")
        layout.prop(mytool, "texture_width")
        layout.prop(mytool, "texture_height")
        layout.separator()
        layout.label(text="BAKE TYPE")
        layout.prop(mytool, "bake_type")
        layout.separator()
        layout.label(text="TEXTURE FORMAT")
        layout.prop(mytool, "img_format")
#        layout.prop(mytool, "my_float")
#        layout.prop(mytool, "my_float_vector", text="")
#        layout.prop(mytool, "my_string")
#        layout.prop(mytool, "my_path")
        layout.separator()
        layout.operator("wm.hello_world")
#        layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    WM_OT_HelloWorld,
    OBJECT_MT_CustomMenu,
    OBJECT_PT_CustomPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()