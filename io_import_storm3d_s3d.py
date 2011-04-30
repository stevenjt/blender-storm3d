#!/usr/bin/python3
#
# io_import_storm3d_s3d.py
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
    "name": "Import: Storm3D S3D",
    "author": "Steven J Thompson",
    "version": (0, 0, 1),
    "blender": (2, 5, 7),
    "api": 36079,
    "location": "File > Import ",
    "description": "Imports S3D files which are used in the Frozenbyte Storm3D engine",
    "warning": "Work in progress",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy, struct, os

class s3dFile():
    def readFromFile(self, type, number = 0): 
        if type == "c":
            charString = ''
            char = ''
            while(char != '\x00'):
                char = bytes.decode(struct.unpack("c", f.read(1))[0])
                if char != '\x00':
                    charString += str(char)
            return charString
        elif type == "B":
            return struct.unpack(number * "B", f.read(number))[0]
        elif type == "H":
            return struct.unpack(number * "H", f.read(number * 2))
        elif type == "L":
            return struct.unpack(number * "L", f.read(number * 4))
        elif type == "f":
            return struct.unpack(number * "f", f.read(number * 4))
        elif type == "i":
            return struct.unpack(number * "i", f.read(number * 4))


    def skipFromFile(self, skipBytes): 
        f.seek(f.tell() + skipBytes)

    def getTexNum(self):
        return self.num_tex

    def getMatNum(self):
        return self.num_mat

    def getObjNum(self):
        return self.num_obj

    def open(self, filename):
        global f
        try:
            f = open(filename, "rb")
        except:
            print("S3D file not found")
            exit()

        if os.name == "posix":
            ## POSIX, use forward slash
            slash = "/"
        else:
            ## Probably Windows, use backslash
           slash = "\\"

        current_dir = filename.split(slash)[:-1]
        ModelFileName = filename.split(slash)[-1].split(".")[0]
        current_dir = slash.join(current_dir) + slash

        self.file_type = ""
        for x in range(4):
            self.file_type += bytes.decode(struct.unpack("c", f.read(1))[0])

        self.version = self.readFromFile("i", 1)[0]
        self.num_tex = self.readFromFile("H", 1)[0]
        self.num_mat = self.readFromFile("H", 1)[0]
        self.num_obj = self.readFromFile("H", 1)[0]
        self.num_lig = self.readFromFile("H", 1)[0]
        self.num_hel = self.readFromFile("H", 1)[0]
        self.bone = self.readFromFile("H", 1)[0]
        self.bone = self.readFromFile("H", 1)[0]

        self.textures = []
        self.materials = []

        ## for all the textures in the file
        for t in range(self.getTexNum()):

            ## read texture filename
            string = self.readFromFile("c")

            ## put the texture into the textures list
            self.textures.append(string)
            
            texid = self.readFromFile("i", 1)
            texStartFrame = self.readFromFile("H", 1)[0]
            texFrameChangeTime = self.readFromFile("H", 1)[0]
            
            texDynamic = self.readFromFile("B", 1)

        ## for all the materials in the file
        for m in range(self.getMatNum()):

            ## read material name
            materialName = self.readFromFile("c")

            ## get the details of the material texture
            materialTextureBase = self.readFromFile("H", 1)[0]
            materialTextureBase2 = self.readFromFile("H", 1)[0]
            materialTextureBump = self.readFromFile("H", 1)[0]
            materialTextureReflection = self.readFromFile("H", 1)[0]

            print(self.version)
            if self.version >= 14:
                materialTextureDistortion = self.readFromFile("H", 1)[0]

            materialColour = self.readFromFile("f", 3)
            materialSelfIllum = self.readFromFile("f", 3)
            materialSpecular = self.readFromFile("f", 3)
            materialSpecularSharpness = self.readFromFile("f", 1)

            materialDoubleSided = self.readFromFile("B", 1)
            materialWireframe = self.readFromFile("B", 1)

            materialReflectionTexgen = self.readFromFile("i", 1)
            materialAlphablendType = self.readFromFile("i", 1)

            materialTransparency = self.readFromFile("f", 1)
            materialGlow = self.readFromFile("f", 1)

            materialScrollSpeed = self.readFromFile("f", 2)
            materialScrollStart = self.readFromFile("B", 1)
            
            ## this isn't quite right
            if materialTextureReflection != 65535:
                pass
                tlayer = self.readFromFile("f", 2)

            mat = bpy.data.materials.new(materialName)
            tex = bpy.data.textures.new(materialName, type = 'IMAGE')
            texSlot = mat.texture_slots.add()
            texSlot.texture = tex
            texSlot.texture_coords = 'UV'
            try:
                image = bpy.data.images.load(current_dir + self.textures[materialTextureBase])
                tex.image = image
                print("Image loaded from: " + self.textures[materialTextureBase])
            except:
                print("Could not load image id: " + str(materialTextureBase))

            ## append material name to the materials list
            self.materials.append(mat)

        ## for all the objects in the file
        for o in range(self.getObjNum()):

            objectName = self.readFromFile("c")
            objectParent = self.readFromFile("c")

            material_index = self.readFromFile("H", 1)[0]

            ## object position
            objectPositionX = self.readFromFile("f", 1)[0]
            objectPositionY = self.readFromFile("f", 1)[0]
            objectPositionZ = self.readFromFile("f", 1)[0]

            ## object rotation
            objectRotationW = self.readFromFile("f", 1)[0]
            objectRotationX = self.readFromFile("f", 1)[0]
            objectRotationY = self.readFromFile("f", 1)[0]
            objectRotationZ = self.readFromFile("f", 1)[0]

            ## object scale
            objectScaleX = self.readFromFile("f", 1)[0]
            objectScaleY = self.readFromFile("f", 1)[0]
            objectScaleZ = self.readFromFile("f", 1)[0]

            objectNoCollision = self.readFromFile("B", 1)
            objectNoRender = self.readFromFile("B", 1)
            objectLightObject = self.readFromFile("B", 1)

            objectVertexAmount = self.readFromFile("H", 1)[0]
            objectFaceAmount = self.readFromFile("H", 1)[0]
            
            ## lod and weight stuff, not yet used
            objectLOD = self.readFromFile("B", 1)
            objectWeights = self.readFromFile("B", 1)

            ## Create new mesh in Blender for this object
            mesh = bpy.data.meshes.new(name = str(objectName))

            ## Create new object in Blender for this object
            obj = bpy.data.objects.new(str(objectName), mesh)

            ## Add this object to the Blender scene
            base = bpy.context.scene.objects.link(obj)

            vertex = []
            faces = []
            uvTex = []

            ## For all the vertex in the object
            for n in range(objectVertexAmount):
                vertexPosition = self.readFromFile("f", 3)
                vertexNormal = self.readFromFile("f", 3)
                vertexTextureCoords = self.readFromFile("f", 2)
                vertexTextureCoords2 = self.readFromFile("f", 2)

                ## store vertex data
                ## y and z are swapped due to differences between which axis is 'up' between Blender and Storm3D
                vertex.append((vertexPosition[0], vertexPosition[2], vertexPosition[1]))

                ## store texture coord data
                uvTex.append(vertexTextureCoords)

            ## For all the faces in the object
            for n in range(objectFaceAmount):
                faces.append(self.readFromFile("H", 3))

            ## For all the weights in the object
            for n in range(objectVertexAmount):
                bone1 = self.readFromFile("i", 1)[0]
                bone2 = self.readFromFile("i", 1)[0]
                weight1 = self.readFromFile("B", 1)
                weight2 = self.readFromFile("B", 1)

            ## there can be other stuff here for lights and helpers

            ## Send data to the mesh in Blender
            mesh.from_pydata(vertex, [], faces)
            mesh.update()

            ## Set the material in Blender
            mesh.materials.append(self.materials[0])

        ## Close the S3D file
        f.close()

        # Open the B3D file
        try:
            b3dpath = current_dir + ModelFileName + ".b3d"
            f = open(b3dpath, "rb")
        except:
            print("B3D file not found")
            exit()

## Blender script/addon stuff
from bpy.props import StringProperty
from io_utils import ImportHelper

class ImportS3D(bpy.types.Operator, ImportHelper):
    bl_idname = "import.s3d"
    bl_label = "Import S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default="*.s3d", options={'HIDDEN'})

    def execute(self, context):
        s3d = s3dFile()
        s3d.open(self.filepath)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ImportS3D.bl_idname, text="Storm3D S3D (.s3d)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
