# The program collages .jpg pictures from a specific folder. Each picture is generated from an automated microscopy
# screening and contains indication of the position of the picture on a laboratory plate (with rows indicated with letters
# and columns indicated with numbers). The pictures are assembled together at the expected position according to the
# file name. Constant parameters are the number of pictures per row/column, the spacing between pictures (horizontal
# and vertical) and the size of each picture in the collage. See parameters below.

import glob
import os
from PIL import Image, ImageDraw, ImageFont

#Parameters
WIDTH = 500
HEIGHT = 500
ROW = 4
COL = 6
SPACING_X = 20
SPACING_Y = 20
ANNOTATION_TOP = 125
ANNOTATION_LEFT = 300
CORRECTING = 50
TEXT_SIZE_OUT = 80
TEXT_SIZE_IN = 80

# Read all .jpg files at specific location
filepaths = glob.glob(r'C:\Users\ValentinoGiarola\PycharmProjects\HRB\pictures\*.jpg')
print(filepaths)

# First a list of xy coordinates is created according to parameters to be later used for picture assembly
def plate_xy():
    plate = []
    for y in range(ROW):
        for x in range(COL):
            if x == 0 and y == 0:
                xy = (x * WIDTH + ANNOTATION_LEFT, y * HEIGHT + ANNOTATION_TOP)
            if x >= 1 and y == 0:
                xy = (x * WIDTH + x * SPACING_X + ANNOTATION_LEFT, y * HEIGHT + ANNOTATION_TOP)
            if x == 0 and y >=1:
                xy = (x * WIDTH + ANNOTATION_LEFT, y * HEIGHT + y * SPACING_Y + ANNOTATION_TOP)
            if x >= 1 and y >= 1:
                xy = (x*WIDTH+x*SPACING_X + ANNOTATION_LEFT, y*HEIGHT+y*SPACING_Y + ANNOTATION_TOP)
            plate.append(xy)
    return plate

# A dictionary is created associating different row/col column locations (with row indicated as letters and column as
# numbers) with xy values of those locations. The resulting dictionary is printed on the screen.

def plate_dic():
    dicts = {}
    keys = []
    for i in range(ROW):
        for j in range(COL):
            coordinate = chr(ord('A') + i) + '0' + str(j+1)
            keys.append(coordinate)
    plate = plate_xy()
    for key in keys:
        for value in plate:
            dicts[key] = value
            plate.remove(value)
            break
    print(dicts)
    return dicts

def annotation_read():
    annotation = {}
    # generates the keys for the dictionary annotation
    keys = []
    for i in range(COL):
        coordinate = 'T ' + str(i + 1)
        keys.append(coordinate)
    for j in range(ROW):
        coordinate = 'L ' + str(j+1)
        keys.append(coordinate)
    values = []

    with open('annotation.txt') as f:
        while True:
            line = f.readline()
            element=line.strip()
            if not line:
                break
            values.append(element)
    for key in keys:
        for value in values:
            annotation[key] = value
            values.remove(value)
            break
    f.close()
    print(annotation)
    return annotation

def annotation_ext(image):
    annotation_names = annotation_read()
    print(annotation_names)
    annotation_xy = {}
    for item in annotation_names.items():
        print(item)
        key_split = item[0].split()
        if key_split[0] == 'T' and int(key_split[1]) == 1:
            annotation_xy[item[0]] = (ANNOTATION_LEFT + WIDTH/2 -len(item[1])/2, 20)
        if key_split[0] == 'T' and int(key_split[1]) > 1:
            annotation_xy[item[0]] = ((int(key_split[1])-1) * (WIDTH+SPACING_X) + WIDTH/2 -len(item[1])/2 + ANNOTATION_LEFT , 20)
        if key_split[0] == 'L' and int(key_split[1]) == 1:
            annotation_xy[item[0]] = (0, HEIGHT/2 + ANNOTATION_TOP)
        if key_split[0] == 'L' and int(key_split[1]) > 1:
            annotation_xy[item[0]] = (0, (int(key_split[1]) - 1) * (HEIGHT+SPACING_Y) + HEIGHT/2 + ANNOTATION_TOP)
    print(annotation_xy)
    myFont = ImageFont.truetype(r"C:\Users\ValentinoGiarola\PycharmProjects\HRB\fonts\arial.ttf", TEXT_SIZE_OUT)
    d1=ImageDraw.Draw(image)
    for item in annotation_names.items():
        key_split = item[0].split()
        if key_split[0] == 'T':
            d1.text((annotation_xy.get(item[0])), item[1], anchor='mt', font=myFont, align='left', fill=(0, 0, 0))
        if key_split[0] == 'L':
            d1.text((annotation_xy.get(item[0])), item[1], anchor='lm', align='right', font=myFont, fill=(0, 0, 0))
    return image

def annotation_int(image):
    coordinates=plate_xy()
    for i in range(len(coordinates)):
        x, y = coordinates[i]
        coordinates[i]= (x+20, y+HEIGHT*0.8)
    myFont = ImageFont.truetype(r"C:\Users\ValentinoGiarola\PycharmProjects\HRB\fonts\arial.ttf", TEXT_SIZE_IN)
    d1 = ImageDraw.Draw(image)
    z = 0
    with open('annotation2.txt') as f:
        while True:
            line = f.readline()
            element=line.strip()
            if not line or z >= ROW*COL:
                break
            else:
                left, top, right, bottom = d1.textbbox((coordinates[z]), element, font=myFont)
                d1.rectangle((left - 5, top - 5, right + 5, bottom + 5), fill="white")
                d1.text((coordinates[z]), element, font=myFont, fill="black")
                z += 1
    return image
def assembly():
    # create a new image with the size of the merged pictures
    image_merged = Image.new('RGB', (COL * WIDTH + COL * SPACING_X + ANNOTATION_LEFT, ROW * HEIGHT + ROW * SPACING_Y + ANNOTATION_TOP), (250, 250, 250))

    i = 0
    names = []
    # create plate coordinates for pictures
    plate = plate_xy()
    plate2 = plate_dic()
    # read each image, resize and assemble according to plate coordinates
    for fp in filepaths:
        head, tail = os.path.split(str(fp))
        file_name = tail
        file_name_parts = file_name.split('_')
        position = file_name_parts[5][:3]
        if position in plate2:
            image_temp = Image.open(fp)
            image_resized = image_temp.resize((WIDTH, HEIGHT))
            pos_x, pos_y = plate2[position]
            image_merged.paste(image_resized, (pos_x, pos_y))
    return image_merged

    # save merged file and visualize it

def main():
    image_merged = assembly()
    image_merged.save(".\merged\merged_image.jpg", "JPEG")
    image_merged.show()
    im1 = annotation_ext(image_merged)
    im1.show()
    im1.save("annotated1.jpg", "JPEG")
    im2 = annotation_int(image_merged)
    im2.show()
    im2.save("annotated2.jpg", "JPEG")

if __name__ == '__main__':
    main()