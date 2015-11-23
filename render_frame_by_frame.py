import bpy
import math
import bpy
import mathutils
import pydevd
import numpy as np


def color_vertex(obj, vert, color):
    """Paints a single vertex where vert is the index of the vertex
    and color is a tuple with the RGB values."""

    mesh = obj.data
    scn = bpy.context.scene

    #check if our mesh already has Vertex Colors, and if not add some... (first we need to make sure it's the active object)
    scn.objects.active = obj
    obj.select = True
    if mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.active
    else:
        vcol_layer = mesh.vertex_colors.new()

    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop_vert_index = mesh.loops[loop_index].vertex_index
            if vert == loop_vert_index:
                vcol_layer.data[loop_index].color = color


def calc_timepoint(new_frame=bpy.context.scene.frame_current):
    bpy.context.scene.frame_current = new_frame
    print('before clearing coloring...')
    try:
        for vertex in bpy.data.objects['out'].data.vertex_layers_float['mean_visibility_values'].data:
            vertex.value = 1.0

    except KeyError:
        bpy.data.objects['out'].data.vertex_layers_float.new('mean_visibility_values')

    try:
        for vertex in bpy.data.objects['out'].data.vertex_layers_int['number_of_values_per_vertex'].data:
            vertex.value = 0

    except KeyError:
        bpy.data.objects['out'].data.vertex_layers_int.new('number_of_values_per_vertex')

    try:
        for vertex in bpy.data.objects['out'].data.vertex_colors['Col'].data:
            vertex.color = (1.0, 1.0, 1.0)

    except KeyError:
        bpy.data.objects['out'].data.vertex_colors.new(name='Col')


    try:
        for vertex in bpy.data.objects['out'].data.vertex_layers_float['R'].data:
            vertex.value = 1.0

    except KeyError:
        bpy.data.objects['out'].data.vertex_layers_float.new('R')

    try:
        for vertex in bpy.data.objects['out'].data.vertex_layers_float['G'].data:
            vertex.value = 1.0

    except KeyError:
        bpy.data.objects['out'].data.vertex_layers_float.new('G')

    try:
        for vertex in bpy.data.objects['out'].data.vertex_layers_float['B'].data:
            vertex.value = 1.0

    except KeyError:
        bpy.data.objects['out'].data.vertex_layers_float.new('B')


    print('Finish clearing coloring')
    print('Calculating new colors for frame '+str(new_frame))
    brain_obj = bpy.data.objects['out']
    vertex_to_color_list = []
    for cur_obj in bpy.data.objects['patches_parent'].children:
        print('checking '+cur_obj.name+' patch.')
        cur_visibility = cur_obj['visibility']
        if cur_visibility > 0:
            print(cur_obj.name+' patch is ON. updating parameters')
            cur_patch_color = (cur_obj['R']*cur_visibility+1*(1-cur_visibility), cur_obj['G']*cur_visibility+1*(1-cur_visibility),
                               cur_obj['B']*cur_visibility+1*(1-cur_visibility))
            if cur_patch_color != (1, 1, 1):
                vertex_to_color_list.extend(cur_obj['vertices_list'])
                for vertex_ind in cur_obj['vertices_list']:
                    # pydevd.settrace()
                    cur_R = bpy.data.objects['out'].data.vertex_layers_float['R'].data[vertex_ind].value
                    cur_G = bpy.data.objects['out'].data.vertex_layers_float['G'].data[vertex_ind].value
                    cur_B = bpy.data.objects['out'].data.vertex_layers_float['B'].data[vertex_ind].value

                    cur_color = (cur_R, cur_G, cur_B)
                    new_r = cur_color[0]*brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value+cur_patch_color[0] * 1
                    new_g = cur_color[1]*brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value+cur_patch_color[1] * 1
                    new_b = cur_color[2]*brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value+cur_patch_color[2] * 1
                    brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value += 1
                    new_r /= brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value
                    new_g /= brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value
                    new_b /= brain_obj.data.vertex_layers_int['number_of_values_per_vertex'].data[vertex_ind].value
                    # bpy.data.objects['out'].data.vertex_colors['Col'].data[vertex_ind].color = (new_r, new_g, new_b)
                    bpy.data.objects['out'].data.vertex_layers_float['R'].data[vertex_ind].value = new_r
                    bpy.data.objects['out'].data.vertex_layers_float['G'].data[vertex_ind].value = new_g
                    bpy.data.objects['out'].data.vertex_layers_float['B'].data[vertex_ind].value = new_b

                    # color_vertex(bpy.data.objects['out'], vertex_ind, bpy.data.objects['out'].data.vertex_colors['Col'].data[vertex_ind].color)

    vertex_to_color_list = list(set(vertex_to_color_list))
    # for vertex_ind in vertex_to_color_list:
    #     color_vertex(bpy.data.objects['out'], vertex_ind, color)
    f = np.load('/media/ohadfel/Elements/Abeles/blender_lookup_table.npy')
    for vertex_ind in vertex_to_color_list:
        for face_ind in f[vertex_ind, :]:
            if face_ind == -1:
                break
            cur_R = bpy.data.objects['out'].data.vertex_layers_float['R'].data[vertex_ind].value
            cur_G = bpy.data.objects['out'].data.vertex_layers_float['G'].data[vertex_ind].value
            cur_B = bpy.data.objects['out'].data.vertex_layers_float['B'].data[vertex_ind].value
            brain_obj.data.vertex_colors['Col'].data[face_ind].color = (cur_R, cur_G, cur_B)


pathAndName = 'C://abeles//brain3inBlender//Frames1//framesT18'
startFrame = 1
# endFrame = bpy.context.scene.frame_end+1
endFrame = 2785
for i in range(startFrame, endFrame):
    print("Rendering frame "+str(i)+" of "+str(bpy.context.scene.frame_end))
    bpy.context.scene.frame_current = i
    try:
        if bpy.types.Scene.new_object_creation == True:
            print('Calculating the new time point')
            calc_timepoint(i)
    except:
        pass

    fileName = pathAndName+str(i)
    bpy.context.scene.render.filepath = fileName
    bpy.ops.render.render(write_still=True)
