import numpy as np
import bpy

total_num_of_verts = len(bpy.data.objects['out'].data.vertices)
lookup_table = np.ones((total_num_of_verts, 20), dtype=np.int)*-1
last_inds = np.zeros((total_num_of_verts, 1), dtype=np.int)

mesh = bpy.data.objects['out'].data
for poly in mesh.polygons:
    for loop_index in poly.loop_indices:
        loop_vert_index = mesh.loops[loop_index].vertex_index
        lookup_table[loop_vert_index, last_inds[loop_vert_index]] = loop_index
        last_inds[loop_vert_index] += 1
print('FINISH!!!')
np.save('/media/ohadfel/Elements/Abeles/blender_lookup_table.npy', lookup_table)
