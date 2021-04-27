'''
@Description:
            主要功能：将mark工具标注的xml标注转为json标注，方便labelme查看及生成coco格式数据
            关键处理：1.汉字转拼音 pypinyin工具包；2.检测标注类别错标并调整类别，modify_type函数；
                    3.xml结构转为coco结构，transform_xml_2labelme函数
@author: lijianqing
@date: 2020/11/11 13:19
'''
from xml.etree import ElementTree as ET
import multiprocessing
import pypinyin
import time
import json
import os

def pinyin(word):#zhangsan = pinyin('张三')
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s
def modify_type(type,points_l):
    type_index = {0:'none',1:'point',2:'line',3:'polygon',4:'bndbox',5:'ellipse'}
    if len(points_l)<3:#长度为0，1,2的
        if type!='ellipse' and type!='bndbox':#类别不为圆和bndbox的情况下按长度设置类别，长度为0的都为none,长度为1的都是点，长度为2的都是线，
            type=type_index[len(points_l)]
        elif len(points_l)!=2:
            type=type_index[len(points_l)]#类别为圆或bndbox，但长度小于2的，按长度设置类别，长度为0的都为none,长度为1的都是点，
        else:#类别为圆或bndbox，长度为2的，符合圆或bndbox的标准，不做修改
            type=type
    elif len(points_l)<4:#长度为3的
        if type!='line':#类别不为line的按多边形处理
            type=type_index[len(points_l)]
        else:#类别为line的，符合line标准，不做修改
            type=type
    else:#长度大于或等于4的
        if type!='line' and type!='polygon':#类别既不是line,也不是多边形的，按多边形polygon处理
            type=type_index[3]
        else:#类别为线，或多边形的，不做修改
            type=type
    return type
def transform_xml_2labelme(para):
    xml_path, save_json, image_name = para
    transform_shapes_dic = {'polygon':'polygon','line':'linestrip','bndbox':'rectangle','point':'circle','ellipse':'circle'}
    tree = ET.parse(xml_path)
    root_node = tree.getroot()
    imagePath = '{}.jpg'.format(image_name)
    xmlPath = root_node[0].text
    print("debug", xml_path)
    imageWidth =int(root_node[4][0].text) #json_obj['imageWidth']=0
    imageHeight = int(root_node[4][1].text)#json_obj['imageHeight']=0
    imageDepth = int(root_node[4][2].text)#null
    imageLabeled = root_node[3].text
    time_Labeled = root_node[2].text
    shapes = []
    for i in root_node[1][0]:
        dic_instance = {}
        dic_instance['label']=pinyin(i[0].text)
        points_l = []
        point_axis = []
        flag = 0
        #print('kd----------:',i[1].text,'--',i[2].tag)#像素宽度
        for j in i[2].iter(): #j = 0 is sub-root
            if flag !=0:
                #print('j.text,shape:',j.text,i[2].tag,i[1].text,)
                point_axis.append(float(j.text))
                if len(point_axis)==2:
                    points_l.append(point_axis)
                    point_axis=[]
            else:
                flag = 1
        xml_tag = i[2].tag
        #modify type xml
        i_2_tag = modify_type(xml_tag,points_l)
        #point2circle
        if i_2_tag=='point' and len(points_l)==1:
            r = int(i[1].text)/2
            x,y = points_l[0]
            r_x = x+r
            r_y = y+r
            points_l.append([r_x,r_y])
            i_2_tag = 'ellipse'

        #2 labelme json after modify type in xml
        try:
            dic_instance['shape_type']=transform_shapes_dic[i_2_tag]
        except:
            print('标注类别为空或错误，请检测。',i[2].tag,xml_path)
        dic_instance['width']=i[1].text
        dic_instance['points'] = points_l
        dic_instance['group_id']=''
        dic_instance['flags']={}#i[3].text#state
        try:
            dic_instance['level'] = i[4].text#'level'
        except:
            #print('无照片严重程度')
            a=0
        try:
            dic_instance['mlevel'] = i[5].text#'mlevel'
        except:
            #print('无缺陷严重程度')
            a=0
        try:
            dic_instance['describe'] = i[6].text#'describe'
        except:
            #print('无描述')
            a=0
        if len(points_l)>0:#标注长度大于0时为可用的有效标注
            shapes.append(dic_instance)
    dic_all = {}
    dic_all['version']='1.0'
    dic_all['flags']={}
    dic_all['shapes']= shapes
    dic_all['imagePath']=imagePath
    dic_all['xmlPath']=xmlPath
    print('正在处理：',imagePath)
    dic_all['imageData'] = None
    dic_all['imageHeight']=imageHeight
    dic_all['imageWidth']=imageWidth
    dic_all['imageDepth']= imageDepth
    dic_all['imageLabeled']=imageLabeled
    dic_all['time_Labeled']=time_Labeled
    with open(save_json,"w",encoding="utf-8") as f:
        content=json.dumps(dic_all,ensure_ascii=False)
        f.write(content)
        f.close()

def main(local_path,save_path,process_num=4):
    pool = multiprocessing.Pool(processes=process_num) # 创建进程个数
    paras = []
    for i in os.listdir(local_path):
        xml_path = os.path.join(local_path,i)#xml_path
        # image_name = i.split('.xml')[0]
        if i not in ['deployment.xml','encodings.xml','misc.xml','modules.xml','profiles_settings.xml','vcs.xml','workspace.xml']:
            image_name = i.split('.xml')[0]
            # print('**********',image_name)
            json_path = os.path.join(save_path,'{}.json'.format(image_name))
            paras.append((xml_path, json_path, image_name))


    pool.map(transform_xml_2labelme, paras)  #第二个para必须是可iter


    pool.close()
    pool.join()

if __name__ == "__main__":
    s = time.time()
    # if not os.path.exists('../jsons'):
    #     os.makedirs('../jsons')
    xml_outputs_path = r'H:\Project_Jack\Face_mask_detection\data_processing\xml_all'
    json_save_path = r'H:\Project_Jack\Face_mask_detection\data_processing\jsons'
    process_num = 4
    main(xml_outputs_path,json_save_path,process_num)
    print('run time:', time.time()-s)
