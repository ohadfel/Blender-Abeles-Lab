import numpy as np
import bpy

cortexAndCerebellumStr = "out"   # This is the name of the cortex + cerebellum object
output_full_path = '/media/ohadfel/Elements/Abeles/blender_lookup_table.npy'

total_num_of_verts = len(bpy.data.objects[cortexAndCerebellumStr].data.vertices)
lookup_table = np.ones((total_num_of_verts, 20), dtype=np.int)*-1
last_inds = np.zeros((total_num_of_verts, 1), dtype=np.int)

mesh = bpy.data.objects['out'].data
for poly in mesh.polygons:
    for loop_index in poly.loop_indices:
        loop_vert_index = mesh.loops[loop_index].vertex_index
        lookup_table[loop_vert_index, last_inds[loop_vert_index]] = loop_index
        last_inds[loop_vert_index] += 1
print('FINISH!!!')
np.save(output_full_path, lookup_table)
