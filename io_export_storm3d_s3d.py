#!/usr/bin/python3
#
# io_export_storm3d_s3d.py
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
    "name": "Export: Storm3D S3D",
    "author": "Steven J Thompson",
    "version": (0, 0, 1),
    "blender": (2, 5, 7),
    "api": 36079,
    "location": "File > Export ",
    "description": "Exports data to S3D files which are used in the Frozenbyte Storm3D engine",
    "warning": "Unfinished, Work in progress",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy, struct, os

class s3dFile():
    def writeToFile(self, type, value = 0, endString = True): 
        if type == "s":
            if endString == True:
                value = value + "\x00"
            f.write(bytes(value, "UTF-8"))
        elif type == "i":
            string = struct.pack("i", value)
            f.write(string)
        elif type == "f":
            string = struct.pack("f", value)
            f.write(string)
        elif type == "H":
            string = struct.pack("H", value)
            f.write(string)
        elif type == "h":
            string = struct.pack("h", value)
            f.write(string)
        elif type == "L":
            string = struct.pack(">L", value)
            f.write(string)
        elif type == "B":
            string = struct.pack("B", value)
            f.write(string)

    def getObjectsOfType(self, objType):
        objectList = []
        for o in bpy.data.objects:
            if o.type == objType:
                objectList.append(bpy.data.objects[o.name])
        return objectList

    def getTextures(self):
        return bpy.data.textures

    def getMaterials(self):
        return bpy.data.materials

    def open(self, filename, getB3D):
        global f

        ####################
        ## S3D file
        ####################

        ## Create and open the target S3D file
        try:
            f = open(filename, "wb")
        except:
            print("S3D file not found")

        if os.name == "posix":
            ## POSIX, use forward slash
            slash = "/"
        else:
            ## Probably Windows, use backslash
           slash = "\\"

        current_dir = filename.split(slash)[:-1]
        ModelFileName = filename.split(slash)[-1].split(".")[0]
        current_dir = slash.join(current_dir) + slash

        file_type = "S3D0"
        version = 14
        self.writeToFile("s", file_type, False)
        self.writeToFile("i", version)

        textures = self.getTextures()
        materials = self.getMaterials()
        objects = self.getObjectsOfType('MESH')
        self.writeToFile("H", len(textures))
        self.writeToFile("H", len(materials))
        self.writeToFile("H", len(objects))

        lights = 0
  #      lights = self.getObjectsOfType('LAMP')
        self.writeToFile("H", lights)

        num_hel = 0
        boneid = 0
        self.writeToFile("H", num_hel)
        self.writeToFile("i", boneid)

        for t in textures:
            ## textureName
            self.writeToFile("s", t.name)

            ## texId
            self.writeToFile("L", 0)

            ## texStartFrame
            self.writeToFile("H", 0)

            ## texFrameChangeTime
            self.writeToFile("H", 0)

            ## texDynamic
            self.writeToFile("B", 0)

        for m in materials:

            ## write material name
            self.writeToFile("s", m.name)

            ## write the details

            ## materialTextureBase
            self.writeToFile("h", 0)

            ## materialTextureBase2
            materialTextureBase2 = 1
            self.writeToFile("h", materialTextureBase2)

            ## materialTextureBump
            self.writeToFile("h", 0)

            ## materialTextureReflection
            materialTextureReflection = 5
            self.writeToFile("h", materialTextureReflection)

            if version >= 14:
                ## materialTextureDistortion
                self.writeToFile("h", 1)

            ## materialColour
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)

            ## materialSelfIllum
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)

            ## materialSpecular
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)

            ## materialSpecularSharpness
            self.writeToFile("f", 1)

            ## materialDoubleSided
            self.writeToFile("B", 1)

            ## materialDoubleWireframe
            self.writeToFile("B", 1)

            ## materialReflectionTexgen
            self.writeToFile("i", 1)

            ## materialAlphablendType
            self.writeToFile("i", 1)

            ## materialTransparency
            self.writeToFile("f", 1)

            if version >= 12:
                ## materialGlow
                self.writeToFile("f", 1)

            if version >= 13:
                ## materialScrollSpeed
                self.writeToFile("f", 1)
                self.writeToFile("f", 1)

                ## materialScrollStart
                self.writeToFile("B", 1)

            if materialTextureBase2 >= 0:
                self.writeToFile("f", 1)
                self.writeToFile("f", 1)

            if materialTextureReflection >= 0:
                self.writeToFile("f", 1)
                self.writeToFile("f", 1)

        for o in objects:

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.quads_convert_to_tris()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
            ## objectName
            self.writeToFile("s", o.name)
            ## objectParent
            self.writeToFile("s", o.name)

            ## material_index
            self.writeToFile("H", 1)

            ## object position
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)

            ## object rotation
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)

            ## object scale
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)
            self.writeToFile("f", 1)

            ## objectNoCollision
            self.writeToFile("B", 1)
            ## objectNoRender
            self.writeToFile("B", 1)
            ## objectLightObject
            self.writeToFile("B", 1)

            vertex = o.data.vertices
            faces = o.data.faces

            ## objectVertexAmount
            self.writeToFile("H", len(vertex))
            ## objectFaceAmount
            self.writeToFile("H", len(faces))

            ## objectLOD
            self.writeToFile("B", 1)

            ## objectWeights
            objectWeights = 0
            self.writeToFile("B", objectWeights)

            for v in vertex:
                ## vertexPosition
                self.writeToFile("f", v.co[0])
                self.writeToFile("f", v.co[2])
                self.writeToFile("f", v.co[1])

                ## vertexNormal
                self.writeToFile("f", v.normal[0])
                self.writeToFile("f", v.normal[1])
                self.writeToFile("f", v.normal[2])

                ## vertexTextureCoords
                self.writeToFile("f", 0.1)
                self.writeToFile("f", 0.1)

                ## vertexTextureCoords2
                self.writeToFile("f", 0.1)
                self.writeToFile("f", 0.1)

            for fa in faces:
                ## face index
                self.writeToFile("H", fa.vertices[0])
                self.writeToFile("H", fa.vertices[1])
                self.writeToFile("H", fa.vertices[2])

            if objectWeights == True:
                pass
                ## objectWeights




        ## Close the S3D file
        f.close()

## Blender script/addon stuff
from bpy.props import StringProperty, BoolProperty
from io_utils import ExportHelper

class ExportS3D(bpy.types.Operator, ExportHelper):
    bl_idname = "export.s3d"
    bl_label = "Export S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default = "*.s3d", options = {'HIDDEN'})

    getB3D = BoolProperty(name = "Export B3D (Bones)", description = "Export data to a B3D file", default = True)

    def execute(self, context):
        s3d = s3dFile()
        s3d.open(self.filepath, self.getB3D)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ExportS3D.bl_idname, text="Storm3D S3D (.s3d)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()
