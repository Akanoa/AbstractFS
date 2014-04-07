import os, sys

CLASS_PATH = os.path.join(os.path.dirname(__file__), '..', '..','classes')
sys.path.append(CLASS_PATH)


from AbstractFS import  fs

with open("L:/test.txt", "w") as f:
    f.write("test grandeur nature")

fs.copy("L:/test.txt","ftp://tartampion@10.1.8.241/test.txt")

try:
    fs.move("ftp://tartampion@10.1.8.241/test.txt", "L:/test.txt.cpy")


    print open("L:/test.txt.cpy").readlines()[0]

    fs.delete("L:/test.txt")
    fs.delete("L:/test.txt.cpy")

except Exception, e:
    print "Exception",e



