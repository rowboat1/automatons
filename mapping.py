from PIL import Image

def set_map(size,map_file):
    im = Image.open(map_file)

    num_x = im.width // size
    num_y = im.height // size

    with open("themap.txt","w") as newfile:
        for y in range(num_y):
            for x in range(num_x):
                blues = 0
                greens = 0
                # Moves a block over the png and takes a majority vote as 
                # to whether this block should be green or blue
                for ny in range(y * size, (y + 1) * size):
                    for nx in range(x * size, (x + 1) * size):
                        pix = im.getpixel((nx, ny))[:3]
                        if pix == (0, 0, 255):
                            blues += 1
                        elif pix == (0, 255, 0):
                            greens += 1
                if greens == 0 and blues == 0:
                    raise Exception("The map file provided wasn't" \
                                    "valid. You must provide a map" \
                                    " with only green #00ff00 and blue"\
                                    " #0000ff pixels.")
                if greens >= blues:
                    newfile.write("g")
                else:
                    newfile.write("b")
            newfile.write("\n")
