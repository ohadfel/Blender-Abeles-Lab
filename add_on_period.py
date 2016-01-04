# Show all functional objects
import bpy

timeOfApearence = 105
timeOfDisapearence = 115
developmentTimeInSec = 0
bottomLimitForActivity = 0.4
fps = 24


def insert_keyframe_to_custom_prop(obj, prop_name, value, keyframe):
    bpy.context.scene.objects.active = obj
    obj.select = True
    obj[prop_name] = value
    obj.keyframe_insert(data_path='['+'"'+prop_name+'"'+']', frame=keyframe)

new_object_creation = bpy.types.Scene.new_object_creation
allObjects = bpy.data.objects

functionalObjects = [obj for obj in allObjects if (obj.name[0] == 'I' and obj.name[1] == 'D' and obj.name[2] == '_')]
# functionalMat = [m for m in bpy.data.materials if (m.name[0] == 'c' and m.name[1] == 'N' and m.name[2] == 'c')]

for curObj in functionalObjects:
    if curObj.type == 'EMPTY' and new_object_creation:
        # critical point number 1
        insert_keyframe_to_custom_prop(curObj, 'visibility', 0, timeOfApearence*fps-2)
        insert_keyframe_to_custom_prop(curObj, 'visibility', bottomLimitForActivity, timeOfApearence*fps-1)

        # critical point number 4
        current_time = timeOfDisapearence*fps + 1
        insert_keyframe_to_custom_prop(curObj, 'visibility', 0, current_time)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting keyframes for "One" visibility~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # critical point number 2
        insert_keyframe_to_custom_prop(curObj, 'visibility', 1, (timeOfApearence + developmentTimeInSec)*fps+1)

        # critical point number 3
        insert_keyframe_to_custom_prop(curObj, 'visibility', 1, (timeOfDisapearence - developmentTimeInSec)*fps-1)
    else:
        curObj.hide_render = False
        curObj.keyframe_insert(data_path="hide_render", index=-1, frame=timeOfApearence*fps)
        curMat = curObj.active_material
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=timeOfApearence*fps)
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=timeOfDisapearence*fps)

        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 1
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=(timeOfApearence + developmentTimeInSec)*fps+1)
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=(timeOfDisapearence - developmentTimeInSec)*fps-1)