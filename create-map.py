from PIL import Image

im = Image.open("usa2.png")

size = 12

num_x = 800//size
num_y = 800//size


with open("themap.txt","w") as newfile:
    for y in range(num_y):
        for x in range(num_x):
            tally = []
            for ny in range(y*size,(y+1)*size):
                for nx in range(x*size,(x+1)*size):
                    pix = im.getpixel((nx,ny))
                    if pix == (0,0,255):
                        tally.append("b")
                    elif pix == (0,255,0):
                        tally.append("g")
            if tally.count("g") >= tally.count("b"):
                newfile.write("g")
            else:
                newfile.write("b")
        newfile.write("\n")
