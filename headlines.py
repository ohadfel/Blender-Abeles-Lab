import bpy
import csv
import math



# Set constants
fps = 24
# pathToCSV = "C:\\abeles\\brain3inBlender\\CSVfiles\\headlines_20_noRod.csv"      # This is the path for the CSV File.
pathToCSV = "D:\\abeles\\brain3inBlender\\CSVfiles\\headlines_20_noRod.csv"      # This is the path for the CSV File.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ read CSV file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Col0 = "str"
Col1 = "startTime"
Col2 = "endTime"

# Create a dictionary with the CSV file content.
mydictionary = {Col0: [], Col1: [], Col2: []}
csvFile = csv.reader(open(pathToCSV, "rt"))
i = 0

for row in csvFile:
    mydictionary[Col0].append(row[0])
    mydictionary[Col1].append(float(row[1]))
    mydictionary[Col2].append(float(row[2]))
    i += 1

scene = bpy.context.scene
obj = scene.objects['SecondaryHeadline']


def recalculate_text(scene):
    startList = mydictionary[Col1]
    endList = mydictionary[Col2]
    currentTime = scene.frame_current/fps
    for ii in range(0, len(startList)):
        if (currentTime >= startList[ii]) and (currentTime < endList[ii]):
            obj.data.body = mydictionary[Col0][ii]


bpy.app.handlers.frame_change_pre.append(recalculate_text)
