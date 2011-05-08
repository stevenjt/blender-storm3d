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
    def openFile(self, filename):
        ## Open the S3D file
        try:
            self.f = open(filename, "rb")
        except:
            print("S3D file not found")

    def closeFile(self):
        self.f.close()

    def readFromFile(self, type, number = 0): 
        if type == "c":
            charString = ''
            char = ''
            while(char != '\x00'):
                char = bytes.decode(struct.unpack("c", self.f.read(1))[0])
                if char != '\x00':
                    charString += str(char)
            return charString
        elif type == "B":
            return struct.unpack(number * "B", self.f.read(number))[0]
        elif type == "H":
            return struct.unpack(number * "H", self.f.read(number * 2))
        elif type == "h":
            return struct.unpack(number * "h", self.f.read(number * 2))
        elif type == "L":
            return struct.unpack(number * ">L", self.f.read(number * 4))
        elif type == "f":
            return struct.unpack(number * "f", self.f.read(number * 4))
        elif type == "i":
            return struct.unpack(number * "i", self.f.read(number * 4))


    def skipFromFile(self, skipBytes): 
        self.f.seek(f.tell() + skipBytes)

    def open(self, filename, getB3D):

        ####################
        ## S3D file
        ####################

        self.openFile(filename)

        if os.name == "posix":
            ## POSIX, use forward slash
            slash = "/"
        else:
            ## Probably Windows, use backslash
           slash = "\\"

        current_dir = filename.split(slash)[:-1]
        ModelFileName = filename.split(slash)[-1].split(".")[0]
        current_dir = slash.join(current_dir) + slash

        file_type = ""
        for x in range(4):
            file_type += bytes.decode(struct.unpack("c", self.f.read(1))[0])

        version = self.readFromFile("i", 1)[0]

        textureCount = self.readFromFile("H", 1)[0]
        materialCount = self.readFromFile("H", 1)[0]
        objectCount = self.readFromFile("H", 1)[0]
        lightCount = self.readFromFile("H", 1)[0]
        helperCount = self.readFromFile("H", 1)[0]

        boneid = self.readFromFile("i", 1)[0]

        textures = []
        materials = []

        ## for all the textures in the file
        for t in range(textureCount):

            ## read texture filename
            textureName = self.readFromFile("c")

            ## put the texture into the textures list
            textures.append(textureName)
            
            texId = self.readFromFile("L", 1)
            texStartFrame = self.readFromFile("H", 1)[0]
            texFrameChangeTime = self.readFromFile("H", 1)[0]
            texDynamic = self.readFromFile("B", 1)

        ## for all the materials in the file
        for m in range(materialCount):

            ## read material name
            materialName = self.readFromFile("c")

            ## get the details of the material texture
            materialTextureBase = self.readFromFile("h", 1)[0]
            materialTextureBase2 = self.readFromFile("h", 1)[0]
            materialTextureBump = self.readFromFile("h", 1)[0]
            materialTextureReflection = self.readFromFile("h", 1)[0]

            if version >= 14:
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

            if version >= 12:
                materialGlow = self.readFromFile("f", 1)

            if version >= 13:
                materialScrollSpeed = self.readFromFile("f", 2)
                materialScrollStart = self.readFromFile("B", 1)

            if materialTextureBase2 >= 0:
                tlayer = self.readFromFile("f", 2)
            
            if materialTextureReflection >= 0:
                tlayer = self.readFromFile("f", 2)

            mat = bpy.data.materials.new(materialName)
            tex = bpy.data.textures.new(materialName, type = 'IMAGE')
            texSlot = mat.texture_slots.add()
            texSlot.texture = tex
            texSlot.texture_coords = 'UV'
            try:
                image = bpy.data.images.load(current_dir + textures[materialTextureBase])
                tex.image = image
                print("Image loaded from: " + textures[materialTextureBase])
            except:
                print("Could not load image id: " + str(materialTextureBase))

            ## append material name to the materials list
            materials.append(mat)

        ## for all the objects in the file
        for o in range(objectCount):

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
                uvTex.append((vertexTextureCoords[0], -(vertexTextureCoords[1])))

            ## For all the faces in the object
            for n in range(objectFaceAmount):
                face = self.readFromFile("H", 3)
                faces.append(face)

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

            bpy.context.scene.objects.active = obj
            bpy.ops.mesh.uv_texture_add()
            uv = obj.data.uv_textures.active
            faces = obj.data.faces

            for face, i in enumerate(uv.data):
                i.uv1 = uvTex[faces[face].vertices[0]]
                i.uv2 = uvTex[faces[face].vertices[1]]
                i.uv3 = uvTex[faces[face].vertices[2]]

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.normals_make_consistent()
            bpy.ops.object.mode_set(mode = 'OBJECT')

            ## Set GLSL
            bpy.context.scene.game_settings.material_mode = 'GLSL'

            ## Set all the 3d viewports to textured
            for a in bpy.context.screen.areas:
                if a.type == 'VIEW_3D':
                    a.active_space.viewport_shade = 'TEXTURED'

            ## Set the material in Blender
            mesh.materials.append(materials[material_index])

        bpy.ops.object.select_all(action = 'SELECT')
        bpy.ops.object.shade_smooth()
        bpy.ops.object.select_all(action = 'DESELECT')

        ## for all the lights in the file
        for l in range(lightCount):
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
        for h in range(helperCount):
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
        self.closeFile()

        ####################
        ## B3D file
        ####################

        ## Open the B3D file if it is to be read
        b3dLoaded = False
        if getB3D == True:
            try:
                b3dpath = current_dir + ModelFileName + ".b3d"
                self.openFile(b3dpath)
                b3dLoaded = True
            except:
                print("B3D file not found")

        if b3dLoaded == True:
            b3dfile_type = ""
            for x in range(5):
                b3dfile_type += bytes.decode(struct.unpack("c", self.f.read(1))[0])

            b3dBoneId = self.readFromFile("i", 1)[0]
            b3dBoneCount = self.readFromFile("i", 1)[0]

            for b in range(b3dBoneCount):

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
            self.closeFile()

## Blender script/addon stuff
from bpy.props import StringProperty, BoolProperty
from io_utils import ImportHelper

class ImportS3D(bpy.types.Operator, ImportHelper):
    bl_idname = "import.s3d"
    bl_label = "Import S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default = "*.s3d", options = {'HIDDEN'})

    getB3D = BoolProperty(name = "Import B3D (Bones)", description = "Import data from the B3D file if present", default = True)

    def execute(self, context):
        s3d = s3dFile()
        s3d.open(self.filepath, self.getB3D)
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
