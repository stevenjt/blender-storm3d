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
        elif type == "h":
            return struct.unpack(number * "h", f.read(number * 2))
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

    def getLigNum(self):
        return self.num_lig

    def getHelNum(self):
        return self.num_hel

    def open(self, filename):
        global f

        ####################
        ## S3D file
        ####################

        ## Open the S3D file
        try:
            f = open(filename, "rb")
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

        self.file_type = ""
        for x in range(4):
            self.file_type += bytes.decode(struct.unpack("c", f.read(1))[0])

        self.version = self.readFromFile("i", 1)[0]

        self.num_tex = self.readFromFile("H", 1)[0]
        self.num_mat = self.readFromFile("H", 1)[0]
        self.num_obj = self.readFromFile("H", 1)[0]
        self.num_lig = self.readFromFile("H", 1)[0]
        self.num_hel = self.readFromFile("H", 1)[0]

        self.boneid = self.readFromFile("i", 1)[0]
        print("s3d bone id: " + str(self.boneid))

        self.textures = []
        self.materials = []

        ## for all the textures in the file
        for t in range(self.getTexNum()):

            ## read texture filename
            textureName = self.readFromFile("c")

            ## put the texture into the textures list
            self.textures.append(textureName)
            
            texId = self.readFromFile("L", 1)
            texStartFrame = self.readFromFile("H", 1)[0]
            texFrameChangeTime = self.readFromFile("H", 1)[0]
            
            texDynamic = self.readFromFile("B", 1)

        ## for all the materials in the file
        for m in range(self.getMatNum()):

            ## read material name
            materialName = self.readFromFile("c")
            print(materialName)

            ## get the details of the material texture
            materialTextureBase = self.readFromFile("h", 1)[0]
            materialTextureBase2 = self.readFromFile("h", 1)[0]
            materialTextureBump = self.readFromFile("h", 1)[0]
            materialTextureReflection = self.readFromFile("h", 1)[0]

            print(self.version)
            if self.version >= 14:
                materialTextureDistortion = self.readFromFile("h", 1)[0]

            materialColour = self.readFromFile("f", 3)
            materialSelfIllum = self.readFromFile("f", 3)
            materialSpecular = self.readFromFile("f", 3)
            materialSpecularSharpness = self.readFromFile("f", 1)

            materialDoubleSided = self.readFromFile("B", 1)
            materialWireframe = self.readFromFile("B", 1)

            materialReflectionTexgen = self.readFromFile("i", 1)
            materialAlphablendType = self.readFromFile("i", 1)

            materialTransparency = self.readFromFile("f", 1)

            if self.version >= 12:
                materialGlow = self.readFromFile("f", 1)

            if self.version >= 13:
                materialScrollSpeed = self.readFromFile("f", 2)
                materialScrollStart = self.readFromFile("B", 1)

            print(materialTextureBase2)
            if materialTextureBase2 >= 0:
                tlayer = self.readFromFile("f", 2)
            
            print(materialTextureReflection)
            if materialTextureReflection >= 0:
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

        print(self.getObjNum())
        ## for all the objects in the file
        for o in range(self.getObjNum()):

            objectName = self.readFromFile("c")
            print(objectName)
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
            
            ## lod and weights
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

            if objectWeights == True:
                ## For all the weights in the object
                for n in range(objectVertexAmount):
                    bone1 = self.readFromFile("i", 1)[0]
                    bone2 = self.readFromFile("i", 1)[0]
                    weight1 = self.readFromFile("B", 1)
                    weight2 = self.readFromFile("B", 1)

            ## Send data to the mesh in Blender
            mesh.from_pydata(vertex, [], faces)
            mesh.update()

            ## Set the material in Blender
            mesh.materials.append(self.materials[0])

        ## for all the lights in the file
        for l in range(self.getLigNum()):
            lightName = self.readFromFile("c")
            lightParentName = self.readFromFile("c")

            lightType = self.readFromFile("i", 1)
            lightLensflareIndex = self.readFromFile("i", 1)
            lightColour = self.readFromFile("f", 3)
            lightPosition = self.readFromFile("f", 3)
            lightDirection = self.readFromFile("f", 3)

            lightConeInner = self.readFromFile("f", 1)
            lightConeOuter = self.readFromFile("f", 1)
            lightMultiplier = self.readFromFile("f", 1)
            lightDecay = self.readFromFile("f", 1)

            lightKeyframeEndtime = self.readFromFile("i", 1)

            lightPoskeyAmount = self.readFromFile("B", 2)
            lightDirkeyAmount = self.readFromFile("B", 2)
            lightLumkeyAmount = self.readFromFile("B", 2)
            lightConekeyAmount = self.readFromFile("B", 2)

        ## for all the helpers in the file
        for h in range(self.getHelNum()):
            helpName = self.readFromFile("c")
            helpParentName = self.readFromFile("c")

            helpType = self.readFromFile("i", 1)
            helpPosition = self.readFromFile("f", 3)
            helpOther = self.readFromFile("f", 3)
            helpOther2 = self.readFromFile("f", 3)

            helpKeyframeEndtime = self.readFromFile("i", 1)

            helpPoskeyAmount = self.readFromFile("B", 2)
            helpO1keyAmount = self.readFromFile("B", 2)
            helpO2keyAmount = self.readFromFile("B", 2)

        ## Close the S3D file
        f.close()

        ####################
        ## B3D file
        ####################

        ## Open the B3D file
        try:
            b3dpath = current_dir + ModelFileName + ".b3d"
            f = open(b3dpath, "rb")
            b3dLoaded = True
        except:
            print("B3D file not found")
            b3dLoaded = False

        if b3dLoaded == True:
            self.b3dfile_type = ""
            for x in range(5):
                self.b3dfile_type += bytes.decode(struct.unpack("c", f.read(1))[0])

            self.b3dBoneId = self.readFromFile("i", 1)[0]
            self.b3dBoneCount = self.readFromFile("i", 1)[0]
            print("b3d bone id: " + str(self.b3dBoneCount))

            for b in range(self.b3dBoneCount):

                boneName = self.readFromFile("c")

                ## bone position
                bonePositionX = self.readFromFile("f", 1)[0]
                bonePositionY = self.readFromFile("f", 1)[0]
                bonePositionZ = self.readFromFile("f", 1)[0]

                ## bone rotiation
                boneRotationW = self.readFromFile("f", 1)[0]
                boneRotationX = self.readFromFile("f", 1)[0]
                boneRotationY = self.readFromFile("f", 1)[0]
                boneRotationZ = self.readFromFile("f", 1)[0]

                ## bone original position
                boneOriginalPositionX = self.readFromFile("f", 1)[0]
                boneOriginalPositionY = self.readFromFile("f", 1)[0]
                boneOriginalPositionZ = self.readFromFile("f", 1)[0]

                ## bone original rotiation
                boneOriginalRotationW = self.readFromFile("f", 1)[0]
                boneOriginalRotationX = self.readFromFile("f", 1)[0]
                boneOriginalRotationY = self.readFromFile("f", 1)[0]
                boneOriginalRotationZ = self.readFromFile("f", 1)[0]

                boneMaxAngles = self.readFromFile("f", 6)

                boneLength = self.readFromFile("f", 1)
                boneThickness = self.readFromFile("f", 1)

                boneParentId = self.readFromFile("i", 1)

            self.b3dBoneHelperCount = self.readFromFile("i", 1)[0]

            for h in range(self.b3dBoneHelperCount):

                helperName = self.readFromFile("c")
                helperParent = self.readFromFile("c")

                helperType = self.readFromFile("i", 1)

                ## helper position
                helperPositionX = self.readFromFile("f", 1)[0]
                helperPositionY = self.readFromFile("f", 1)[0]
                helperPositionZ = self.readFromFile("f", 1)[0]

                helperOther1 = self.readFromFile("f", 3)
                helperOther2 = self.readFromFile("f", 3)

                helperEndTime = self.readFromFile("i", 1)[0]
                helperFoo = self.readFromFile("B", 2)
                helperFoo = self.readFromFile("B", 2)
                helperFoo = self.readFromFile("B", 2)

            ## Close the B3D file
            f.close()

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
