io\_scene\_s3d - Importer/Exporter for Storm3D s3d/b3d files
=============================================================

This is a Blender 2.58 add-on that can import Storm3D s3d mesh files and b3d bone files.

Current Features for version 0.3
----------------

S3D/B3D Importer:

 * Mesh data such as vertices and faces.
 * Collision mesh are automatically set to wireframe display mode.
 * UVs for texture mapping.
 * Bone weights imported to vertex groups.
 * Material data.
 * Diffuse and reflection textures. The image files are automatically mapped to the objects using the UVs.
 * Settings panel located at User Preferences -> File. Currently used to set the path to the Data directory which is used for finding files such as textures not present in the same directory of the s3d file being imported.
 * Bone data from B3D file if present. This sets up a Blender armature with the bones using their names, lengths and rotations.

S3D Exporter:

 * Mesh data
 * UVs - This requires the use of seams when UV unwrapping.
 * Bone weights
 * Material data
 * Textures - only image textures.

Install Instructions
--------------------

Put the entire io\_scene\_s3d folder into your blender config addons directory. The config location is found in the following locations:

 * Linux: ~/.blender/2.58/scripts/addons

 * Mac OS X: In Blender.app (in finder right click and select show package contents) under Contents/MacOS/2.58/scripts/addons

    - Addons should really go in ~/Library/Application Support/Blender on Mac OS X. This did not seem to work when I tried it.

 * Windows 7: %APPDATA%\Blender Foundation\Blender\2.58\scripts\addons (pasting that in the search box in the start menu will find the folder).

After this open the File -> User Preferences window and select Add-Ons. The Storm3D S3D addon should be listed under the Import-Export category, tick the box to the right of it and select Save As Default from the bottom of the window. Now the Storm3D import and export options will be available from the File menu whenever you start Blender.
