import json
import os
import cv2
import math
import glob
import multiprocessing
import base64
import time

def save_json(dic, save_path):
    json.dump(dic, open(save_path, 'w',encoding='utf-8'), indent=4)  # indent=4 更加美观显示

def save_new_img(img_np, img_name, xmin, ymin, xmax, ymax, out_path, img_x, img_y):
    # 切图并保存
    xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
    left, top, right, down = 0, 0, 0, 0
    if xmax > img_x:
        right = xmax - img_x
        xmax = img_x
        # print('宽超出了')
    if ymax>img_y:
        down = ymax-img_y
        ymax = img_y
        # print('长超出了')
    if ymin < 0:
        top = abs(ymin)
        ymin= 0
        # print('长负值了')
    if xmin < 0:
        left = abs(xmin)
        xmin = 0
        # print('宽负值了')
    img_crop = img_np[ymin:ymax, xmin:xmax]#不清楚为何切图时y,与x位置互换才正常,补充：w,h表示，可以理解了
    ret = cv2.copyMakeBorder(img_crop, top, down, left, right, cv2.BORDER_CONSTANT, value=(0,0,0))
    cv2.imwrite(os.path.join(out_path, img_name), ret)
    #base64_str = base64.b64encode(ret)#Editbykerry
    #base64_str = base64_str.decode('utf-8')#Editbykerry
    return 0

def count_bbox_size(i):
    points = i['points']
    #points = i
    x, y = zip(*points)
    if i['shape_type']=='circle':
        c = points[0]
        r_p = points[1]
        r = round(math.sqrt((c[0]-r_p[0])**2+(c[1]-r_p[1])**2), 2)
        min_x = round(c[0]-r, 2)
        min_y = round(c[1]-r, 2)
        max_x = round(c[0]+r, 2)
        max_y = round(c[1]+r, 2)
    else:
        min_x = round(min(x), 2)
        min_y= round(min(y), 2)
        max_x = round(max(x), 2)
        max_y = round(max(y), 2)
    # print('max_x,max_y,min_x,min_y',max_x,max_y,min_x,min_y,'---',i['shape_type'])
    return  max_x, max_y, min_x, min_y

def get_new_location(point, mid_point, crop_size=64):
    #x,y不出界时将缺陷放于中心位置
    p_x = point[0]-mid_point[0] + crop_size/2
    p_y = point[1]-mid_point[1] + crop_size/2
    #x,y出界时，移动缺陷框位置。#修改
    dis_x = point[0] - mid_point[0]
    dis_y = point[1] - mid_point[1]
    # if dis_x <0 or dis_y<0:
    #     print('目标尺寸超出指定切图大小了')
    # elif dis_y > crop_size or dis_y>crop_size:
    #     print('目标尺寸超出指定切图大小了')
    if p_x < 0:
        p_x = 0
    if p_y < 0:
        p_y = 0
    if p_x > crop_size:
        p_x = crop_size
    if p_y > crop_size:
        p_y = crop_size
    return [p_x,p_y]
#切图位置超出原图的情况没有处理

def cut_json(file_tuple):
    json_p, img_sourc, crop_szie, out_p_im, cut_label, cccc = file_tuple

    with open(json_p, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    img_n = os.path.join(img_sourc, json_data['imagePath'])#原图像名
    #print('img_n', img_n)
    img_np = cv2.imread(img_n)#原图数据
    #print('img_np', img_np)
    shapes_img_l = {}
    c = 0
    #筛选需要切的label
    for i in json_data['shapes']:
        c+= 1
        if i['label'] in cut_label:
            shapes_img_l[c]=i
    #print(shapes_img_l)
    LLL = []
    mid_point = []
    print(img_n)
    digui(shapes_img_l, cccc, crop_szie, LLL, mid_point)#聚类
    ###core    start
    for kk in range(len(LLL)):
        for kkk in LLL[kk]:
            new_points = []
            for loc in kkk['points']:
                n_p = get_new_location(loc,mid_point[kk],crop_szie)
                new_points.append(n_p)
            kkk['points'] = new_points
            # print('points',kkk['points'],kkk['shape_type'])
        new_name_img = '{}_{}_{}.jpg'.format(mid_point[kk][0],mid_point[kk][1],kk)
        new_name_json = '{}_{}_{}.json'.format(mid_point[kk][0],mid_point[kk][1],kk)
        #生成新的img文件，抠图过程中会出现超出边界的坐标
        source_x_min,source_x_max = mid_point[kk][0]-crop_szie/2,mid_point[kk][0]+crop_szie/2#抠图位置
        source_y_min,source_y_max= mid_point[kk][1]-crop_szie/2,mid_point[kk][1]+crop_szie/2
        x_min,x_max,y_min,y_max = int(source_x_min),int(source_x_max),int(source_y_min),int(source_y_max)
        if x_min > 0 and y_min > 0:
            save_new_img(img_np, new_name_img, x_min, y_min, x_max, y_max, out_p_im, json_data['imageWidth'], json_data['imageHeight'])#Editbykerry
            #生成新的json文件
            # crop_szie_w,crop_szie_h = crop_szie,crop_szie
            def_new_json(json_data, crop_szie, crop_szie, new_name_json, LLL[kk], out_p_im, new_name_img)

def def_new_json(json_data, crop_szie_w, crop_h, new_name, shapes_img, out_p, new_name_img):
    new_json = {}

    new_json['version'] = json_data['version']
    new_json['flags'] = json_data['flags']
    new_json['shapes'] = shapes_img

    new_json['imageData'] = None

    new_json['imageHeight'] = crop_h
    new_json['imageWidth'] = crop_szie_w
    new_json['imagePath'] = new_name_img

    # new_json['imageLabeled'] = json_data['imageLabeled']
    # new_json['imageDepth'] = json_data['imageDepth']
    #new_json['time_Labeled'] = json_data['time_Labeled']

    save_json(new_json, os.path.join(out_p, new_name))
    #print('生成了', os.path.join(out_p, new_name))
    return new_json

def def_dic_element(shapes_img,i,pp):
    dic_element = {}
    dic_element['flags']=i['flags']
    dic_element['group_id']=i['group_id']
    dic_element['label']=i['label']
    dic_element['points'] = pp
    dic_element['shape_type']=i['shape_type']
    dic_element['width']=i['width']
    shapes_img.append(dic_element)
    return shapes_img

cccc = 0

def digui(shapes_img_l, cccc, crop_size, LLL, mid_point):
    cccc += 1
    if len(shapes_img_l)==0:
        #print('递归结束了', cccc-1)
        return 0
    type_i = {}#记录不可以放一起的标注
    allow = []
    max_bbox = []
    #print("开始递归生成新图片、json")
    for i in shapes_img_l:
        #print(shapes_img_l[i])
        max_x, max_y, min_x, min_y = count_bbox_size(shapes_img_l[i])#获取标注的位置
        w, h = max_x-min_x, max_y-min_y
        #与已有点比较距离
        if len(max_bbox)>0:
                a,b,c,d = max_bbox
                mmin_x = min(min_x,c)
                mmin_y = min(min_y,d)
                mmax_x = max(max_x,a)
                mmax_y = max(max_y,b)
                ww, hh = mmax_x-mmin_x, mmax_y-mmin_y
                # print('最大长宽',ww,hh)
                if ww<crop_size and hh <crop_size:
                    max_bbox = mmax_x,mmax_y,mmin_x,mmin_y
                    allow.append(shapes_img_l[i])
                else:
                    type_i[i]=shapes_img_l[i]#不可以放一起的
        else:
            max_bbox = [max_x,max_y,min_x,min_y]
            allow.append(shapes_img_l[i])
    #计算聚类后类别在原图的中心点。
    w,h = max_bbox[0]-max_bbox[2],max_bbox[1]-max_bbox[3]
    mid_x = math.ceil(max_bbox[2]+w/2)
    mid_y = math.ceil(max_bbox[3]+h/2)
    # print('中心点',math.ceil(mid_x),math.ceil(mid_y))
    LLL.append(allow)
    mid_point.append((mid_x,mid_y))
    digui(type_i,cccc,crop_size,LLL,mid_point)

if __name__ == '__main__':
    # out_p为要保存的切图文件夹
    # json_source为labelme格式文件
    # img_p为纯图片文件夹
    out_p      = r'G:\weiyi\About_YOLO\data_processing\xml_coco_yolo\1217_1221\cuts_test'
    json_source= r'G:\weiyi\About_YOLO\data_processing\xml_coco_yolo\1217_1221\1217and1221'
    img_p      = r'G:\weiyi\About_YOLO\data_processing\xml_coco_yolo\1217_1221\img_all'

    cut_label = ['liewen', 'yashang', 'queliao', 'pengshang', 'zhanliao', 'bianxing', 'luomupengshang', 'luomuguoshao']


    jsons = glob.glob('{}/*.json'.format(json_source))

    file_l = []
    for i in jsons:
        file_l.append((i, img_p, 768, out_p, cut_label, cccc))
    pool = multiprocessing.Pool(processes=8) # 创建进程个数
    start_time = time.time()
    pool.map(cut_json, file_l)
    print('run time:', time.time() - start_time)
    pool.close()
    pool.join()
#切512图半小时
# 切768图219秒
