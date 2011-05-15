#!/usr/bin/python3
#
# io_scene_s3d
#
# Copyright (C) 2011 Steven J Thompson
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Storm3D S3D",
    "author": "Steven J Thompson",
    "version": (0, 1),
    "blender": (2, 5, 7),
    "api": 36079,
    "location": "File > Import-Export ",
    "description": "Import and Export S3D files which are used in the Frozenbyte Storm3D engine",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy
from . import fileclasses
from bpy.props import StringProperty, BoolProperty
from io_utils import ImportHelper, ExportHelper

class ImportS3D(bpy.types.Operator, ImportHelper):
    bl_idname = "import.s3d"
    bl_label = "Import S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default = "*.s3d", options = {'HIDDEN'})

    getB3D = BoolProperty(name = "Import B3D (Bones)", description = "Import data from the B3D file if present", default = False)
    switchGLSL = BoolProperty(name = "Use GLSL", description = "Allow the script to switch to GLSL shading", default = True)

    def execute(self, context):
        s3d = fileclasses.S3DFile()
        s3d.open(self.filepath, self.switchGLSL)
        b3d = fileclasses.B3DFile()
        b3d.open(self.filepath, self.getB3D)
        return {'FINISHED'}

class ExportS3D(bpy.types.Operator, ExportHelper):
    bl_idname = "export.s3d"
    bl_label = "Export S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default = "*.s3d", options = {'HIDDEN'})

    getB3D = BoolProperty(name = "Export B3D (Bones)", description = "Export data to a B3D file", default = True)

    def execute(self, context):
        s3d = fileclasses.S3DFile()
        s3d.write(self.filepath)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportS3D.bl_idname, text="Storm3D S3D (.s3d)")

def menu_func_export(self, context):
    self.layout.operator(ExportS3D.bl_idname, text="Storm3D S3D (.s3d)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
