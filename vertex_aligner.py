bl_info = {
    "name": "Vertex Aligner",
    "author": "Silik1",
    "version": (1, 0),
    "blender": (3, 00, 0),
    "location": "View3D > Sidebar > Align Tab",
    "description": "Aligns the selected vertices along a straight line formed by two reference vertices",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

import bpy
import bmesh

stored_coords = []


class StoreCoordsOperator(bpy.types.Operator):
    bl_idname = "object.store_coords_operator"
    bl_label = "Stores coordinates"

    def execute(self, context):
        global stored_coords
        obj = context.active_object

        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v for v in bm.verts if v.select]

            if len(selected_verts) == 2:
                stored_coords = [obj.matrix_world @ v.co for v in selected_verts]
                self.report({'INFO'}, "Stored coordinates")
            else:
                self.report({'WARNING'}, "Select exactly 2 vertices")
        else:
            self.report({'WARNING'}, "Select a mesh object in edit mode")

        return {'FINISHED'}


class AlignVertsOperator(bpy.types.Operator):
    bl_idname = "object.align_verts_operator"
    bl_label = "Align vertices"

    def execute(self, context):
        global stored_coords
        obj = context.active_object

        if not stored_coords or len(stored_coords) != 2:
            self.report({'WARNING'}, "First store the coordinates of two vertices")
            return {'CANCELLED'}

        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v for v in bm.verts if v.select]

            if len(selected_verts) > 0:
                v1, v2 = stored_coords
                direction = (v2 - v1).normalized()

                for vert in selected_verts:
                    proj_vector = (obj.matrix_world @ vert.co - v1).project(direction)
                    vert.co = obj.matrix_world.inverted() @ (v1 + proj_vector)

                bmesh.update_edit_mesh(obj.data)
                self.report({'INFO'}, "Aligned vertices")
            else:
                self.report({'WARNING'}, "Select at least one vertex to align")
        else:
            self.report({'WARNING'}, "Select a mesh object in edit mode")

        return {'FINISHED'}


class AlignVertexPanel(bpy.types.Panel):
    bl_label = "Align vertices to a line"
    bl_idname = "OBJECT_PT_align_vertex"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Vertex Aligner"

    def draw(self, context):
        layout = self.layout
        layout.operator(StoreCoordsOperator.bl_idname, text="Stores coordinates")
        layout.operator(AlignVertsOperator.bl_idname, text="Align selected vertices")


def register():
    bpy.utils.register_class(StoreCoordsOperator)
    bpy.utils.register_class(AlignVertsOperator)
    bpy.utils.register_class(AlignVertexPanel)


def unregister():
    bpy.utils.unregister_class(StoreCoordsOperator)
    bpy.utils.unregister_class(AlignVertsOperator)
    bpy.utils.unregister_class(AlignVertexPanel)


if __name__ == "__main__":
    register()
