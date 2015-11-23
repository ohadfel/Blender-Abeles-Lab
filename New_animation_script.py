#animation script

import bpy
import csv
import math


#    | devTime  |upState| devTime |
#               *********
#          *                *
#    *                            *
#    1          2       3         4

# Set constants
# pathToCSV = "D:\\abeles\\brain3inBlender\\CSVfiles\\Time18ms_patchANDrod.csv"      # This is the path for the CSV File.
pathToCSV = "//media//ohadfel//DISKONKEYS//abeles//superTime18errorWlinePatches.csv"
# pathToCSV = "/media/ohadfel/Elements/Abeles/Time20correct3.csv"    # This is the path for the CSV File.
# pathToCSV = "D:\\abeles\\brain3inBlender\\CSVfiles\\Time20correct_patchAndRod_pink.csv"      # This is the path for the CSV File.
# pathToCSV = "//media//ohadfel//Elements//Abeles//Time20correct.csv"      # This is the path for the CSV File.
fps = 24
suspendInSec = 7.5          # time before first event starts.  Should be coordinated with ballAndText script  MA
# msPerSample = 2             # sampling period of data  MA
developmentTimeInSec = 0  # MA: was 1.5, but time was comletely wrong! CANNOT BE 0 as then objects do not disappear
upStateTime = 20
overlap = 0.95
useHide = False
emissionNodeName = 'MyColor'
diffuseNodeName = 'MyColor1'
Diffusion_Emission_ratio = 0.3
bottomLimitForActivity = 0.4
# pathToSRT = "C:\\Users\\Felz\\Desktop\\ohad\\blender_movie_script\\subtitles.srv"


def insert_keyframe_to_custom_prop(obj, prop_name, value, keyframe):
    bpy.context.scene.objects.active = obj
    obj.select = True
    obj[prop_name] = value
    obj.keyframe_insert(data_path='['+'"'+prop_name+'"'+']', frame=keyframe)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ prePattern period ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print('Starting Animation script.')
new_object_creation = bpy.types.Scene.new_object_creation

allObjects = bpy.data.objects
functionalObjects = []

for obj in allObjects:
    if obj.name[0] == 'I' and obj.name[1] == 'D' and obj.name[2] == '_':
        functionalObjects.append(obj)

for curObj in functionalObjects:
    if curObj.type == 'EMPTY':
        insert_keyframe_to_custom_prop(curObj, 'visibility', 0, 1.0)
        if suspendInSec != 0:
            insert_keyframe_to_custom_prop(curObj, 'visibility', 0, fps*suspendInSec)
    else:
        curMat = curObj.active_material
        if suspendInSec == 0:
            if useHide:
                curObj.hide_render = True
                curObj.keyframe_insert(data_path="hide_render", index=-1, frame=1)
            curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
            #         obj.active_material.alpha = 0
            curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=1.0)
            #         obj.active_material.keyframe_insert(data_path="alpha", frame=1.0, index=-1)

        else:
            curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
            #       obj.active_material.alpha = 1
            curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=1.0)
            #        obj.active_material.keyframe_insert(data_path="alpha", frame=1.0, index=-1)
            curObj.hide_render = False
            curObj.keyframe_insert(data_path="hide_render", index=-1, frame=1)

            curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
            #       obj.active_material.alpha = 0
            curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=fps*suspendInSec)
            #       obj.active_material.keyframe_insert(data_path="alpha", frame=fps*suspendInSec, index=-1)
            if useHide:
                curObj.hide_render = True
                curObj.keyframe_insert(data_path="hide_render", index=-1, frame=fps*suspendInSec+1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ read CSV file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Col0 = "ind"                                # This is index of the object.
Col1 = "Moshe_index"                        # This is the original index number which is used for the object's name.
Col2 = "Time"                               # This is the time of change in the object material.
Col3 = "Transparency"                       # This is the Transparency level of object material.
Col4 = "R"                                  # This is the red component of the base color of the object.(Emission)
Col5 = "G"                                  # This is the green component of the base color of the object.(Emission)
Col6 = "B"                                  # This is the blue component of the base color of the object.(Emission)
Col7 = "Rd"                                 # This is the red component of the base color of the object.(Diffuse)
Col8 = "Gd"                                 # This is the green component of the base color of the object.(Diffuse)
Col9 = "Bd"                                 # This is the blue component of the base color of the object.(Diffuse)

# Create a dictionary with the CSV file content.
mydictionary = {Col0: [], Col1: [], Col2: [], Col3: [], Col4: [], Col5: [], Col6: [],Col7: [], Col8: [], Col9: []}
csvFile = csv.reader(open(pathToCSV, "rt"))
i=0

for row in csvFile:
    mydictionary[Col0].append(i)
    mydictionary[Col1].append(row[0])
    mydictionary[Col2].append(row[1])
    mydictionary[Col3].append(row[2])
    mydictionary[Col4].append(row[3])
    mydictionary[Col5].append(row[4])
    mydictionary[Col6].append(row[5])
    if len(row) == 9:
        mydictionary[Col7].append(row[6])
        mydictionary[Col8].append(row[7])
        mydictionary[Col9].append(row[8])
    else:
        mydictionary[Col7].append(mydictionary[Col4][-1])
        mydictionary[Col8].append(mydictionary[Col5][-1])
        mydictionary[Col9].append(mydictionary[Col6][-1])
    i += 1


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create objects ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
numOfLines = len(mydictionary['Moshe_index'])
## scale by times per sample MA
# for ii in range (0,numOfLines):
#    mydictionary['Time'][ii] = str(msPerSample*float(mydictionary['Time'][ii]))

for ii in range(0, numOfLines):
    print(ii)
    # print('Time= '+str(mydictionary['Time'][ii]))  # debug print MA
    # Keyframe

    # ****************************************************************Onset calc************************************************************
    onsetTime =fps * (suspendInSec)+fps*(float(mydictionary['Time'][ii])*(developmentTimeInSec*2+upStateTime)*(1-overlap))
    print(onsetTime)

    #    | devTime  |upState| devTime |
    #               *********
    #          *                *
    #    *                            *
    #    1          2       3         4
    # ****************************************************************Onset calc************************************************************

    curObjStr = 'ID_'+mydictionary['Moshe_index'][ii]
    curObj = bpy.data.objects[curObjStr]
    if curObj.type == 'MESH' or not new_object_creation:
        curMat = curObj.active_material
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
    #    curObj.active_material.alpha = 0

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting keyframes for zero visibility~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # critical point number 1
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=onsetTime-2)
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = bottomLimitForActivity
        if useHide:
            curObj.hide_render = False
            curObj.keyframe_insert(data_path="hide_render", index=-1, frame=onsetTime-1)
            print('~~~~~~~~~~UseHIDE==TRUE~~~~~~~~~~')
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = bottomLimitForActivity
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=onsetTime-1)
    # critical point number 4
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
        if useHide:
            curObj.hide_render = True
            curObj.keyframe_insert(data_path="hide_render", index=-1, frame=onsetTime + (upStateTime + developmentTimeInSec * 2) * fps + 1)
            print('~~~~~~~~~~UseHIDE==TRUE~~~~~~~~~~')
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = 0
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=onsetTime + (upStateTime + developmentTimeInSec * 2) * fps + 1)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting keyframes for "One" visability~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = float(mydictionary['Transparency'][ii])
    #    curObj.active_material.alpha = float(mydictionary['Transparency'][ii])

    # critical point number 2
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=onsetTime + developmentTimeInSec * fps)
    # critical point number 3
        curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].keyframe_insert(data_path="default_value", frame=onsetTime + (upStateTime + developmentTimeInSec) * fps)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting RGB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if mydictionary['R'][ii][0].isdigit():
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ setting keyframes for new RGB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # curObj.active_material.diffuse_color=(float(mydictionary['R'][ii]),float(mydictionary['G'][ii]),float(mydictionary['B'][ii]))
            # print(ii)

            # Emission Color settings
            curMat.node_tree.nodes[emissionNodeName].inputs['Color'].keyframe_insert(data_path="default_value", frame=onsetTime - 1)
            # curMat.node_tree.nodes['MyColor'].inputs['Color'].keyframe_insert(data_path="default_value",frame=onsetTime+(upStateTime+developmentTimeInSec)*fps+1)

            print('Object-' + str(ii))
            print('RGB')
            print(mydictionary['R'][ii])
            print(mydictionary['G'][ii])
            print(mydictionary['B'][ii])

            diffuse_color = (float(mydictionary['R'][ii]), float(mydictionary['G'][ii]), float(mydictionary['B'][ii]), 1)

            curMat.node_tree.nodes[emissionNodeName].inputs[0].default_value = diffuse_color
            curMat.node_tree.nodes[emissionNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime)
            curMat.node_tree.nodes[emissionNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime + (upStateTime + developmentTimeInSec) * fps)

            # Diffusion Color settings
            curMat.node_tree.nodes[diffuseNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime - 1)
            # curMat.node_tree.nodes['MyColor'].inputs['Color'].keyframe_insert(data_path="default_value",frame=onsetTime+(upStateTime+developmentTimeInSec)*fps+1)
            print('RdGdBd')
            print(mydictionary['Rd'][ii])
            print(mydictionary['Gd'][ii])
            print(mydictionary['Bd'][ii])

            diffuse_color = (float(mydictionary['Rd'][ii]), float(mydictionary['Gd'][ii]), float(mydictionary['Bd'][ii]), 1)
            curMat.node_tree.nodes[diffuseNodeName].inputs[0].default_value = diffuse_color
            curMat.node_tree.nodes[diffuseNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime)
            curMat.node_tree.nodes[diffuseNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime + (upStateTime + developmentTimeInSec) * fps)

            curMat.node_tree.nodes['Diffusion_Emission_ratio'].inputs[0].default_value = Diffusion_Emission_ratio
            curMat.node_tree.nodes[diffuseNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime)
            curMat.node_tree.nodes[diffuseNodeName].inputs[0].keyframe_insert(data_path="default_value", frame=onsetTime + (upStateTime + developmentTimeInSec) * fps)

    elif curObj.type =='EMPTY' and new_object_creation:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting keyframes for zero visibility~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # critical point number 1
        insert_keyframe_to_custom_prop(curObj, 'visibility', 0, onsetTime-2)
        insert_keyframe_to_custom_prop(curObj, 'visibility', bottomLimitForActivity, onsetTime-1)

        # critical point number 4
        current_time = onsetTime + (upStateTime + developmentTimeInSec * 2) * fps + 1
        insert_keyframe_to_custom_prop(curObj, 'visibility', 0, current_time)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting keyframes for "One" visibility~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        current_value = float(mydictionary['Transparency'][ii])
        # critical point number 2
        insert_keyframe_to_custom_prop(curObj, 'visibility', current_value, onsetTime + developmentTimeInSec * fps)

        # critical point number 3
        insert_keyframe_to_custom_prop(curObj, 'visibility', current_value, onsetTime + (upStateTime + developmentTimeInSec) * fps)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~setting RGB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if mydictionary['R'][ii][0].isdigit():
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ setting keyframes for new RGB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # curObj.active_material.diffuse_color=(float(mydictionary['R'][ii]),float(mydictionary['G'][ii]),float(mydictionary['B'][ii]))
            # print(ii)

            # Emission Color settings
            # curMat.node_tree.nodes[emissionNodeName].inputs['Color'].keyframe_insert(data_path="default_value", frame=onsetTime - 1)
            # curMat.node_tree.nodes['MyColor'].inputs['Color'].keyframe_insert(data_path="default_value",frame=onsetTime+(upStateTime+developmentTimeInSec)*fps+1)

            print('Object-' + str(ii))
            print('RGB')
            print(mydictionary['R'][ii])
            print(mydictionary['G'][ii])
            print(mydictionary['B'][ii])

            diffuse_color = (float(mydictionary['R'][ii]), float(mydictionary['G'][ii]), float(mydictionary['B'][ii]))
            insert_keyframe_to_custom_prop(curObj, 'R', float(mydictionary['R'][ii]), onsetTime)
            insert_keyframe_to_custom_prop(curObj, 'G', float(mydictionary['G'][ii]), onsetTime)
            insert_keyframe_to_custom_prop(curObj, 'B', float(mydictionary['B'][ii]), onsetTime)

            off_time = onsetTime + (upStateTime + developmentTimeInSec * 2) * fps + 1
            insert_keyframe_to_custom_prop(curObj, 'R', float(mydictionary['R'][ii]), off_time)
            insert_keyframe_to_custom_prop(curObj, 'G', float(mydictionary['G'][ii]), off_time)
            insert_keyframe_to_custom_prop(curObj, 'B', float(mydictionary['B'][ii]), off_time)

print('Animation script finished!')
