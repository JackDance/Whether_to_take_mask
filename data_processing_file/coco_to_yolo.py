import shutil
from collections import defaultdict
import random
from utils import *
import os
import time

def coco_to_yolo(instance, img_folder_path):
    '''
    :param instance: coco json instance
    :param img_folder_path: 图片文件夹路径
    :return: 转为yolo txt在图片路径下
    '''
    name_box_id = defaultdict(list)
    imgs = instance['images']
    annos = instance['annotations']
    for anno in annos:
        id = anno['image_id']
        width, height = imgs[id]['width'], imgs[id]['height']
        name = os.path.join(img_folder_path, imgs[id]['file_name'])
        category = anno['category_id']
        name_box_id[name].append([anno['bbox'], category, width, height])
    for img in imgs:
        name = os.path.join(img_folder_path, img['file_name'])
        file = name[:name.rindex('.')] + '.txt'
        with open(file, 'w') as f:
            if name not in name_box_id:
                continue
            boxes = name_box_id[name]
            for box in boxes:
                x_center = (box[0][0] + box[0][2]/2)/box[2]
                y_center = (box[0][1] + box[0][3]/2)/box[3]
                w = box[0][2]/box[2]
                h = box[0][3]/box[3]
                box_info = "%d %.03f %.03f %.03f %.03f" % (box[1], x_center, y_center, w, h)
                f.write(box_info)
                f.write('\n')

def split_train_val_test(img_folder_path: str, target_folder_path: str, test_ratio=0.1, val_ratio=0.9):
    '''
    :param img_folder_path: image和txt文件所在文件夹路径
    :param datasets_name: 新文件夹名，保存在原文件夹的同级目录
    :param test_ratio: 测试样本占总样本比例
    :param val_ratio: 验证样本占测试样本比例
    :return: 将测试、验证样本从总样本中分开
    '''
    make_folders(target_folder_path)
    total_txt = [txt for txt in os.listdir(img_folder_path) if txt.endswith('.txt')]
    test_txt = random.sample(total_txt, int(len(total_txt)*test_ratio))
    val_txt = random.sample(test_txt, int(len(test_txt)*val_ratio))
    for txt in total_txt:
        if txt in test_txt:
            if txt in val_txt:
                copy(os.path.join(img_folder_path, txt), os.path.join(os.path.join(target_folder_path, 'labels/val'), txt))
            else:
                copy(os.path.join(img_folder_path, txt), os.path.join(os.path.join(target_folder_path, 'labels/test'), txt))
        else:
            copy(os.path.join(img_folder_path, txt), os.path.join(os.path.join(target_folder_path, 'labels/train'), txt))

def copy(src_txt_path, dst_txt_path):
    shutil.copy(src_txt_path, dst_txt_path)
    shutil.copy(src_txt_path.replace('.txt', '.jpg'), dst_txt_path.replace('labels', 'images').replace('.txt', '.jpg'))

def make_folders(base_path):
    folders = ('images/train', 'images/val', 'images/test', 'labels/train', 'labels/val', 'labels/test')
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

if __name__ == '__main__':
    # 读取coco的json文件，转为instance对象
    instance = json_to_instance(json_file_path=r'H:\weiyi\About_YOLO\wai_nei_train_val_6\wai_nei_val_cut_jack.json')
    # 开始转换，填入图像文件夹路径
    if True:
        coco_to_yolo(instance, img_folder_path=r'H:\weiyi\About_YOLO\wai_nei_train_val_6\wai_nei_val_cut_jack')
    else:
    # 按比例分训练、验证、测试集
        time1 = time.time()
        split_train_val_test(img_folder_path=r'H:\Project_Jack\Face_mask_detection\data_processing\mask_dataset\all_mask',
                         target_folder_path=r'H:\Project_Jack\Face_mask_detection\data_processing\mask_dataset_split')
        time2 = time.time()
        print("Convert completed")
        print("total time",time2-time1)








































