from utils import *


class Labelme2Coco:

    def __init__(self, img_folder_path: str, line_pixel=1):
        self.line_pixel = line_pixel
        self.images = []
        self.annotations = []
        self.categories = []
        self.img_id = 0
        self.anno_id = 0
        # 存放所有cls name
        self.classname_to_id = []
        self._init_imgs_and_annos(img_folder_path)
        self._init_categories()
        print('coco instance initialized.')

    def save_coco_json(self, save_path='data_in_coco.json'):
        instance = {'info': 'spytensor created',
                    'license': 'license',
                    'images': self.images,
                    'annotations': self.annotations,
                    'categories': self.categories}
        instance_to_json(instance, save_path)
        # 打印出所有cls, 供配置文件使用
        print('coco file saved.', self.classname_to_id)

    def _init_categories(self):
        self.classname_to_id = sorted(self.classname_to_id)
        for i, cls in enumerate(self.classname_to_id):
            category = {}
            category['id'] = i
            category['name'] = cls
            self.categories.append(category)
        for annotation in self.annotations:
            annotation['category_id'] = self.classname_to_id.index(annotation['category_id'])

    def _init_imgs_and_annos(self, img_folder_path: str):
        files = os.listdir(img_folder_path)
        for file in files:
            # 过滤文件夹和非图片文件
            if not os.path.isfile(os.path.join(img_folder_path, file)) or file[file.rindex('.')+1:] not in IMG_TYPES: continue
            # 对应的json文件
            json_file_path = os.path.join(img_folder_path, file[:file.rindex('.')]+'.json')
            try:
                instance = json_to_instance(json_file_path)
            except Exception as e:
                # 若为无目标图片
                print('%s has no json file in %s.' % (file, img_folder_path))
                instance = create_empty_json_instance(os.path.join(img_folder_path, file))
            instance_clean(instance)
            image = {'id': self.img_id, 'file_name': file}
            image['width'], image['height'] = instance['imageWidth'], instance['imageHeight']
            for obj in instance['shapes']:
                self._init_annos(obj)
            self.images.append(image)
            self.img_id += 1

    def _init_annos(self, obj):
        label = obj['label']
        if label not in self.classname_to_id: self.classname_to_id.append(label)
        annotation = {'id': self.anno_id, 'iscrowd': 0, 'area': 1.0,
                      'image_id': self.img_id,
                      'category_id': label}
        points = obj['points']
        shape_type = obj['shape_type']
        try:
            annotation['segmentation'] = points_to_coco_segmentation(points, shape_type, self.line_pixel)
        except Exception as e:
            annotation['segmentation'] = [[None]]
            print(obj, 'fails in converting into segmentation...')
        annotation['bbox'] = points_to_coco_bbox(points, shape_type)
        self.annotations.append(annotation)
        self.anno_id += 1

if __name__ == '__main__':
    # 通常labelme json文件和图片在一个folder目录
    # obj = Labelme2Coco(img_folder_path='/home/kerry/mnt/mark/apple575/cuts')
    obj = Labelme2Coco(img_folder_path=r'H:\weiyi\About_YOLO\wai_nei_train_val_6\wai_nei_val_cut_jack')
    # coco json导出路径(注意：保存路径最后要加上文件名，比如data_in_coco.json)
    obj.save_coco_json(save_path=r'H:\weiyi\About_YOLO\wai_nei_train_val_6\wai_nei_val_cut_jack.json')


























