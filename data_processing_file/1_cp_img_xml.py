import os
from shutil import copyfile


img_dir = "./img_all/"
xml_dir = "./xml_all/"

if not os.path.exists(img_dir):
    os.makedirs(img_dir)
if not os.path.exists(xml_dir):
    os.makedirs(xml_dir)

for root, dirs, files in os.walk(".", topdown=False):
    
    for name in files:
        print(name)
        sp  = os.path.join(root, name)
        tpi = img_dir + name
        tpx = xml_dir + name

        if (name.split('.')[-1])=='jpg':
            copyfile(sp, tpi)
    
        if (name.split('.')[-1]) == 'xml' and name != 'defect.xml' and name != 'describe.xml' and name != 'setting.xml':
            copyfile(sp, tpx)
    
    for name in dirs:
        print(name)
        sp  = os.path.join(root, name)
        tpi = img_dir + name
        tpx = xml_dir + name

        if (name.split('.')[-1])=='jpg':
            copyfile(sp, tpi)
    
        if (name.split('.')[-1]) == 'xml' and name != 'defect.xml' and name != 'describe.xml' and name != 'setting.xml':
            copyfile(sp, tpx)
    
