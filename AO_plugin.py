import bpy
from datetime import datetime
import os

def bake_texture(obj, width, height, bake_type, img_format):

    image_name = obj.name + '_bake'
    img = bpy.data.images.new(image_name,width,height)

    for mat in obj.data.materials:
        for n in mat.node_tree.nodes:
            if n.name == 'Bake_node' or n.name[:4] == 'GLTF':
                print(n.name[:3])
                mat.node_tree.nodes.remove(n)
                
                
    bpy.context.view_layer.objects.active = obj
    lm =  obj.data.uv_layers.get("UVMap")
    if not lm:
        lm = obj.data.uv_layers.new(name="UVMap")
    lm.active = True
    obj.select_set(True)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin = 0.02)
    bpy.ops.object.editmode_toggle()
    

    i = 0
    for ma in obj.data.materials:
        mat = ma.copy()
        obj.material_slots[i].material = mat
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.location = (-700, 400)
        texture_node.name = 'Bake_node'
        texture_node.select = True
        nodes.active = texture_node
        texture_node.image = img
        i+=1

        
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.bake(type=bake_type,save_mode='EXTERNAL')

    path = os.path.join(bpy.path.abspath("//"), 'bakes')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, image_name+img_format)

    img.save_render(filepath=path)
    
    for mat in obj.data.materials:
        
        if bake_type == "AO":
    
            if bpy.data.node_groups['GLTF Settings']:
                tree = mat.node_tree
                group_node = tree.nodes.new("ShaderNodeGroup")
                group_node.node_tree = bpy.data.node_groups['GLTF Settings']
                group_node.location = (-300, 400)
            else:
                group = bpy.data.node_groups.new(type="ShaderNodeTree", name="GLTF Settings")
                group.inputs.new("NodeSocketFloat", "Occlusion")
                input_node = group.nodes.new("NodeGroupInput")
                
                tree = bpy.context.object.active_material.node_tree
                group_node = tree.nodes.new("ShaderNodeGroup")
                group_node.node_tree = group
                group_node.location = (-300, 400)
         
                        
            n = mat.node_tree.nodes.get("Bake_node")
            mat.node_tree.links.new(n.outputs[0], group_node.inputs[0])
        
        else:
            
            output = mat.node_tree.nodes.get('Material Output')
            bake = mat.node_tree.nodes.get('Bake_node')
            mat.node_tree.links.new(bake.outputs[0], output.inputs[0])
                
                
        

def recursive_baking(object, width, height, bake_type, img_format):
    
    # deselect everything, better safe than sorry
    bpy.ops.object.select_all(action='DESELECT')
    
    # mesh without any children and at least a material => bake
    if object.type == "MESH" and len(object.children) == 0 and len(object.data.materials.items()) > 0:
        object.select_set(True)
        bake_texture(object, width, height, bake_type, img_format)

    # obj with children
    for obj in object.children:
        # obj with children => recursive call
        if len(obj.children) > 0:
            recursive_baking(obj, width, height, bake_type, img_format)
        # mesh with at least a material => bake
        if obj.type == "MESH" and len(obj.data.materials.items()) > 0:
            obj.select_set(True)
            bake_texture(obj, width, height, bake_type, img_format)

        
def recursive_connecting(object, img_format, ao_gltf_export):
    
    # deselect everything, better safe than sorry
    bpy.ops.object.select_all(action='DESELECT')
    
    if object.type == "MESH" and len(object.children) == 0 and len(object.data.materials.items()) > 0:
        object.select_set(True)
        connect(object, img_format, ao_gltf_export)

    for obj in object.children:
        if len(obj.children) > 0:
            recursive_connecting(obj, img_format, ao_gltf_export)
        if obj.type == "MESH" and len(obj.data.materials.items()) > 0:
            obj.select_set(True)
            connect(obj, img_format, ao_gltf_export)


def connect(obj, img_format, ao_gltf_export):

    for mat in obj.data.materials:
        for n in mat.node_tree.nodes:
            if n.name == 'Bake_node':
                
                # build path
                image_name = obj.name + '_bake'
                path = os.path.join(bpy.path.abspath("//"), 'bakes')
                if not os.path.exists(path):
                    os.makedirs(path)
                path = os.path.join(path, image_name+img_format)

                # load image
                img = bpy.data.images.load(path, check_existing=True)
                n.image = img
                
                # if on, connec texture to Occlusion group node
                if (ao_gltf_export == True) :
                    group = bpy.data.node_groups.new(type="ShaderNodeTree", name="GLTF Settings")
                    group.inputs.new("NodeSocketFloat", "Occlusion")
                    input_node = group.nodes.new("NodeGroupInput")
                    
                    tree = bpy.context.object.active_material.node_tree
                    group_node = tree.nodes.new("ShaderNodeGroup")
                    group_node.node_tree = group
                    group_node.location = (-300, 400)
                    
                    mat.node_tree.links.new(n.outputs[0], group_node.inputs[0])
                # else connect texture to material output
                else:
                    output = mat.node_tree.nodes.get('Material Output')
                    bake = mat.node_tree.nodes.get('Bake_node')
                    mat.node_tree.links.new(bake.outputs[0], output.inputs[0])


# select entire hierarchy to export it    


def select_hierarchy(object):
    object.select_set(True)
    for obj in object.children:
        select_hierarchy(obj)
         
def select_hierarchy_to_join(object):
    for obj in object.children:
        select_hierarchy2(obj)
        if len(bpy.context.selected_objects) > 0:
            bpy.ops.object.join()
            bpy.ops.object.select_all(action='DESELECT')
    
def select_hierarchy2(object):
    if object.type == "MESH":
        bpy.context.view_layer.objects.active = object
        object.select_set(True)
    for obj in object.children:
        select_hierarchy2(obj)




bl_info = {
    "name": "Baking Plug-in",
    "description": "Bake entire hierarchies of objects all in one click",
    "author": "elia",
    "version": (0, 1, 0),
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

    ao_gltf_export: BoolProperty(
        name="Export AO for GLTF",
        description="Select this to export the AO for GLTF files",
        default = False
        )
    bake_selected: BoolProperty(
        name="Bake all selected objects",
        description="Select this to bake all the selected objects separately. If not selected, only the active obj will be baked",
        default = True
        )
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
    bake_type: EnumProperty(
        name="",
        description="bake type",
        default='AO',
        items=[('AO', "Ambient Occlusion", "")]
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

        self.report({'INFO'}, "Started Baking")
        
        texture_width = mytool.texture_width
        texture_height = mytool.texture_height
        bake_type = mytool.bake_type
        img_format = mytool.img_format
        bake_selected = mytool.bake_selected
        ao_gltf_export = mytool.ao_gltf_export


        for obj in bpy.context.selected_objects:

            bpy.ops.object.select_all(action='DESELECT')
            select_hierarchy_to_join(obj)
            
            recursive_baking(obj, texture_width, texture_height, bake_type, img_format)
            
            select_hierarchy(obj)
            
            # build path
            path = os.path.join(bpy.path.abspath("//"), 'baked_glbs')
            if not os.path.exists(path):
                os.makedirs(path)
            path = os.path.join(path, obj.name+'.glb')
            
            #export as glb
            bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True)

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
    bl_label = "Blender Batch Bakery"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "BBB"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        layout.label(text="TEXTURE SIZES")

        layout.prop(mytool, "texture_width")
        layout.prop(mytool, "texture_height")
        layout.separator()
        layout.label(text="BAKE TYPE")
        layout.prop(mytool, "bake_type")
        layout.separator()
        layout.label(text="TEXTURE FORMAT")
        layout.prop(mytool, "img_format")
        layout.separator()
        layout.prop(mytool, "bake_selected")
        layout.separator()
        layout.prop(mytool, "ao_gltf_export")
        layout.separator()
        layout.operator("wm.hello_world")
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