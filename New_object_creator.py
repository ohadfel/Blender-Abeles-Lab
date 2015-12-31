# objects creator script
# This is for patches only
# NOTE: layer 2 must be selected before running it
import mathutils
import bpy
import csv
import math
import bmesh
import time


def find_closest_vertex_to_point(patch_location, kd):
    # Find the closest point to the center
    co, index, dist = kd.find(patch_location)
    return co, index, dist


def create_geometry_tree(cortexAndCerbellumStr):
    obj = bpy.data.objects[cortexAndCerbellumStr]

    mesh = obj.data
    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    for ind, v in enumerate(mesh.vertices):
        kd.insert(obj.matrix_world*v.co, ind)

    kd.balance()
    return kd


def find_vertices_list_for_patch(patch_location, patch_radius, kd):
    print('Finding vertices...')
    vertices_list = []
    # Find points within a radius of the 3d cursor
    co_find = patch_location

    for (co, index, dist) in kd.find_range(co_find, rad):
        vertices_list.append(index)
    return vertices_list


def createEmpty(loc, Layers, name, rad):
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=rad, view_align=False, location=loc, layers=Layers)
    bpy.context.object.name = name
    if name != 'patches_parent':
        bpy.data.objects[name].parent = bpy.data.objects['patches_parent']


def insert_keyframe_to_custom_prop(obj, prop_name, value, keyframe):
    bpy.context.scene.objects.active = obj
    obj.select = True
    obj[prop_name] = value
    obj.keyframe_insert(data_path='['+'"'+prop_name+'"'+']', frame=keyframe)


def createSphere(loc, rad, Layers, name):
    bpy.ops.mesh.primitive_uv_sphere_add(ring_count=30, size=rad, view_align=False, enter_editmode=False, location=loc, layers=Layers)
    bpy.ops.object.shade_smooth()

    # Rename object with Moshe's index
    bpy.context.active_object.name = name


def createPatch(boolObj):
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[boolObj]
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")


def patchUnion():
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = 'UNION'
    bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["tempPatch"]
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")

    bpy.data.objects['ID_'+mydictionary['Moshe_index'][ii]].select = False
    bpy.data.objects['tempPatch'].select = True
    bpy.ops.object.delete(use_global=False)
    bpy.data.objects['ID_'+mydictionary['Moshe_index'][ii]].select = True


def cleanPatch():
    # Clear the remaining of the sphere by deleting the vertexes that are radius-0.01 away from the sphere center.
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    sel_mode = bpy.context.tool_settings.mesh_select_mode
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    mesh = bpy.context.object.data

    vert_list = [vert for vert in mesh.vertices]
    for vert in vert_list:
        cond0 = abs(vert.co[0]) == float(mydictionary['Radius'][ii])
        cond1 = abs(vert.co[1]) == float(mydictionary['Radius'][ii])
        cond2 = abs(vert.co[2]) == float(mydictionary['Radius'][ii])

        if cond2 or cond1 or cond0:
            vert.select = True
            vert_list.remove(vert)
            print('clear cape')

        elif math.sqrt(vert.co[0]**2+vert.co[1]**2+vert.co[2]**2) > float(mydictionary['Radius'][ii])-0.01:
            vert.select = True
            vert_list.remove(vert)
#    bpy.ops.object.mode_set(mode='EDIT')
#    me = bpy.context.object.data
#    bm = bmesh.from_edit_mesh(me)
#    vz_list = [v.co[2] for v in bm.verts]
#    if 0.5 in vz_list:
#        bm.verts.remove(bm.verts[vz_list.index(0.5)])
#    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.context.tool_settings.mesh_select_mode = sel_mode
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_face_by_sides()
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)


def createMaterial(name, diffuseColors,transparency):
    # curMat = bpy.data.materials['OrigPatchesMat'].copy()
    curMat = bpy.data.materials['OrigPatchMatTwoCols'].copy()
    curMat.name = name
    bpy.context.active_object.active_material = curMat
    curMat.node_tree.nodes['MyColor'].inputs[0].default_value = diffuseColors
    curMat.node_tree.nodes['MyColor1'].inputs[0].default_value = diffuseColors
    curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = transparency


# Set constants
new_object_creation = True
project_location_on_surface = True
# pathToCSV = "D:\\abeles\\brain3inBlender\\CSVfiles\\Tmplt18_patch_pink.csv"          # This is the path for the CSV File.
pathToCSV = "//media//ohadfel//DISKONKEYS//abeles//superTmplt18errorWline_07Patches.csv"          # This is the path for the CSV File.

layer = 2                      # This is the layer that all sphere and patches objects will be created in.
rodsLayer = 3                  # This is the layer that all rod objects will be created in.
cortexAndCerebellumStr = "out"   # This is the name of the cortex + cerebellum object
innerStructStr = "in"          # This is the name of the inner structures object

print('Starting object creation script.')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ read CSV file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Col0 = "ind"                   # This is index of the object.
Col1 = "Moshe_index"           # This is the original index number which is used for the object's name.
Col2 = "Type_of_obj"           # This is the object shape ('S' for sphere,'P' for patch,'R' for rod).
Col3 = "X"                     # This is the X coordinate for the object. if the object is rod this is the X coordinate for the rod 1' end.
Col4 = "Y"                     # This is the Y coordinate for the object. if the object is rod this is the Y coordinate for the rod 1' end.
Col5 = "Z"                     # This is the Z coordinate for the object. if the object is rod this is the Z coordinate for the rod 1' end.
Col6 = "Radius"                # If the object is a sphere this is the sphere radius, if the object is patch this is the radius for patch creation, if the object is rod this is the thickness of the rod.
Col7 = "R"                     # This is the red component of the base color of the object.
Col8 = "G"                     # This is the green component of the base color of the object.
Col9 = "B"                     # This is the blue component of the base color of the object.
Col10 = "X2"                   # If the object is a rod this is the X coordinate for the rod 2' end.
Col11 = "Y2"                   # If the object is a rod this is the Y coordinate for the rod 2' end.
Col12 = "Z2"                   # If the object is a rod this is the Z coordinate for the rod 2' end.
Col13 = "Patch_On_Surf"        # If the object is a patch write 'out' for patch on the Cortex or Cerebellum, or write 'in' for patch on the inner structures.

# Create a dictionary with the CSV file content.
mydictionary = {Col0: [], Col1: [], Col2: [], Col3: [], Col4: [], Col5: [], Col6: [], Col7: [], Col8: [], Col9: [], Col10: [], Col11: [],
                Col12: [], Col13: []}
csvFile = csv.reader(open(pathToCSV, "rt"))
i = 0

for row in csvFile:
    mydictionary[Col0].append(i)
    mydictionary[Col1].append(row[0])
    mydictionary[Col2].append(row[1])
    mydictionary[Col3].append(row[2])
    mydictionary[Col4].append(row[3])
    mydictionary[Col5].append(row[4])
    mydictionary[Col6].append(row[5])
    mydictionary[Col7].append(row[6])
    mydictionary[Col8].append(row[7])
    mydictionary[Col9].append(row[8])
    mydictionary[Col10].append(row[9])
    mydictionary[Col11].append(row[10])
    mydictionary[Col12].append(row[11])
    mydictionary[Col13].append(row[12])
    i += 1

# create a layer list for the creation of objects.
Layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

# set the layer which we want to create the objects in.
Layers[layer] = True

LayersRods = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
LayersRods[rodsLayer] = True
bpy.types.Scene.new_object_creation = new_object_creation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create objects ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

kd_cortexAndCerbellum = create_geometry_tree(cortexAndCerebellumStr)
kd_innerStruct = create_geometry_tree(cortexAndCerebellumStr)
try:
    print(bpy.data.objects['patches_parent'].name)
except:
    createEmpty((0.0, 0.0, 0.0), Layers, 'patches_parent', 0.01)
    time.sleep(1)

bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)

numOfObjs = len(mydictionary['X'])
for ii in range(0, numOfObjs):
    print(ii)
    # if the current object is sphere or patch create new sphere.
    if mydictionary['Type_of_obj'][ii].lower() == 's':

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create sphere ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        loc = (float(mydictionary['X'][ii]), float(mydictionary['Y'][ii]), float(mydictionary['Z'][ii]))
        rad = float(mydictionary['Radius'][ii])

        createSphere(loc, rad, Layers, 'ID_'+mydictionary['Moshe_index'][ii])

    if mydictionary['Type_of_obj'][ii].lower() == 'p':
        loc = (float(mydictionary['X'][ii]), float(mydictionary['Y'][ii]), float(mydictionary['Z'][ii]))
        rad = float(mydictionary['Radius'][ii])
        if project_location_on_surface:
            co, index, dist = find_closest_vertex_to_point(loc, kd_cortexAndCerbellum)
            loc = co
        if not new_object_creation:
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ create patch ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ old create patch $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

            # create patch on cortex And Cerebellum
            createSphere(loc, rad, Layers, 'tempPatch')
            # Convert the sphere to patch
            print('Convert the sphere to patch')
            # print(len(mydictionary['Patch_On_Surf']))
            createPatch(cortexAndCerebellumStr)
            cleanPatch()

            # create patch on inner brain
            createSphere(loc, rad, Layers, 'ID_'+mydictionary['Moshe_index'][ii])
            createPatch(innerStructStr)

            # Clear the remaining of the sphere by deleting the vertexes that are radius-0.01 away from the sphere center.
            cleanPatch()
            patchUnion()
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ old create patch $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        else:
            # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ new create patch $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            if mydictionary['Patch_On_Surf'][ii] == 'out':
                kd = kd_cortexAndCerbellum
            elif mydictionary['Patch_On_Surf'][ii] == 'in':
                kd = kd_innerStruct
            createEmpty(loc, Layers, 'ID_'+mydictionary['Moshe_index'][ii], rad)
            bpy.data.objects['ID_'+mydictionary['Moshe_index'][ii]]['vertices_list'] = find_vertices_list_for_patch(loc, rad, kd)

        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ new create patch $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # add the rod option
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create rod ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    elif mydictionary['Type_of_obj'][ii].lower() == 'r':
        # add a curve to link them together
        bpy.ops.curve.primitive_bezier_curve_add(layers=LayersRods)
        CurRod = bpy.context.object
        CurRod.data.dimensions = '3D'
        CurRod.data.fill_mode = 'FULL'
        CurRod.data.bevel_depth = float(mydictionary['Radius'][ii])
        CurRod.data.bevel_resolution = 4
        # set first point to centre of sphere1
        CurRod.data.splines[0].bezier_points[0].co = (float(mydictionary['X'][ii]), float(mydictionary['Y'][ii]), float(mydictionary['Z'][ii]))
        CurRod.data.splines[0].bezier_points[0].handle_left_type = 'VECTOR'
        # set second point to centre of sphere2
        CurRod.data.splines[0].bezier_points[1].co = (float(mydictionary['X2'][ii]), float(mydictionary['Y2'][ii]), float(mydictionary['Z2'][ii]))
        CurRod.data.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
        CurRod.location = (0, 0, 0)
        bpy.context.active_object.name = 'ID_'+mydictionary['Moshe_index'][ii]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create and set Material ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # curMaterial = bpy.data.materials.new(mydictionary['Moshe_index'][ii]+'_mat')
    # bpy.context.active_object.active_material=curMaterial
    # curMaterial.diffuse_color=(float(mydictionary['R'][ii]),float(mydictionary['G'][ii]),float(mydictionary['B'][ii]))
    # curMaterial.specular_intensity = 0
    # curMaterial.use_transparency = True
    # curMaterial.alpha = 1
    if bpy.data.objects['ID_'+mydictionary['Moshe_index'][ii]].type != 'EMPTY':
        name = mydictionary['Moshe_index'][ii]+'_mat'
        diffuseColors = (float(mydictionary['R'][ii]), float(mydictionary['G'][ii]), float(mydictionary['B'][ii]), 1)
        createMaterial(name, diffuseColors, 1)

print('Object creation script finished!')
