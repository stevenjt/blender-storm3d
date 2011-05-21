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

import bpy
import struct
import os
from .BinaryFile import BinaryFile

class B3DFile(BinaryFile):

    def addBone(self, object, boneName):
        bpy.context.scene.objects.active = object
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.armature.bone_primitive_add(name=boneName)
        bpy.ops.object.mode_set(mode = 'OBJECT')

    def editBonePosition(self, object, part, boneName, position):
        bpy.context.scene.objects.active = object
        bpy.ops.object.mode_set(mode = 'EDIT')
        if part == 'head':
            object.data.edit_bones[boneName].head = position
        elif part == 'tail':
            object.data.edit_bones[boneName].tail = position
        bpy.ops.object.mode_set(mode = 'OBJECT')

    def connectBones(self, object, bone1, bone2):
        bpy.context.scene.objects.active = object
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.armature.select_all(action = 'DESELECT')
        bone1Object = object.data.edit_bones[bone1]
        bone2Object = object.data.edit_bones[bone2]
        object.data.edit_bones.active = bone1Object
        bone2Object.select = True
        bone2Object.select_head = True
        bone2Object.select_tail= True
        bpy.ops.armature.parent_set(type = 'CONNECTED')
        bpy.ops.armature.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    def prepareMesh(self, object, bones):
        for o in bpy.data.objects:
            if o.type == 'MESH':
                bpy.context.scene.objects.active = o
                bpy.ops.object.modifier_add(type = 'ARMATURE')
                o.modifiers['Armature'].object = object

                for v in o.vertex_groups:
                    v.name = bones[v.name]

    def open(self, path, getB3D):

        ####################
        ## B3D file
        ####################

        ## Open the B3D file if it is to be read
        b3dLoaded = False
        if getB3D == True:
            try:
                ## TEMP
                temp = self.openFile(path, "rb")

                b3dpath = self.getDirectory() + self.getFileName() + ".b3d"
                b3dLoaded = self.openFile(b3dpath, "rb")
            except:
                print("B3D file not found")

        if b3dLoaded == True:
            b3dfile_type = ""
            for x in range(5):
                b3dfile_type += bytes.decode(struct.unpack("c", self.f.read(1))[0])

            b3dBoneId = self.readFromFile("i", 1)[0]
            b3dBoneCount = self.readFromFile("i", 1)[0]

            rig = bpy.data.objects.new(str(b3dBoneId), bpy.data.armatures.new(str(b3dBoneId)))
            bpy.context.scene.objects.link(rig)

            rig.data.draw_type = 'STICK'
            rig.show_x_ray = True

            bones = []
            bonesAndId = {}
            bonesAndParents = []

            for i, b in enumerate(range(b3dBoneCount)):

                boneName = self.readFromFile("c")

                self.addBone(rig, str(boneName))
                bones.append(boneName)
                bonesAndId[str(i)] = boneName

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

                boneLength = self.readFromFile("f", 1)[0]
                boneThickness = self.readFromFile("f", 1)[0]

                boneParentId = self.readFromFile("i", 1)[0]

                parentName = bones[boneParentId]

                self.editBonePosition(rig, 'tail', boneName, (boneOriginalPositionX + 0.001, boneOriginalPositionZ, boneOriginalPositionY))
                self.editBonePosition(rig, 'head', boneName, (boneOriginalPositionX, boneOriginalPositionZ, boneOriginalPositionY))
                if boneParentId != -1:
                    self.editBonePosition(rig, 'head', boneName, rig.data.bones[bones[boneParentId]].tail)

                bonesAndParents.append((boneName, boneParentId))

            for b in bonesAndParents:
                if b[1] != -1:
                    self.connectBones(rig, bones[b[1]], b[0])

            self.prepareMesh(rig, bonesAndId)

            b3dBoneHelperCount = self.readFromFile("i", 1)[0]

            def getHelperType(id):
                if id == 0:
                    return "POINT"
                elif id == 1:
                    return "VECTOR"
                elif id == 2:
                    return "BOX"
                elif id == 3:
                    return "CAMERA"
                elif id == 4:
                    return "SPHERE"

            for h in range(b3dBoneHelperCount):

                helperName = self.readFromFile("c")
                helperParent = self.readFromFile("c")

                helperType = self.readFromFile("i", 1)[0]

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
