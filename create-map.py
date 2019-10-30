from PIL import Image

im = Image.open("usa2.png")

num_x = 800//12
num_y = 800//12


with open("themap.txt","w") as newfile:
    for y in range(num_y):
        for x in range(num_x):
            tally = []
            for ny in range(y*12,(y+1)*12):
                for nx in range(x*12,(x+1)*12):
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
