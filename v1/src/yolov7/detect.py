import torch
import os
import cv2
import random


class YoloModel:
    def __init__(self, conf):
        self.conf = conf
        self.model = torch.hub.load('WongKinYiu/yolov7', 'custom', os.path.join('src', 'yolov7', 'yolov7.pt'),
                                    force_reload=False, trust_repo=True)
        self.img_path = os.path.join('src', 'img.png')

    def reload_model(self, force_reload=True):
        self.model = torch.hub.load('WongKinYiu/yolov7', 'custom', os.path.join('src', 'yolov7', 'yolov7.pt'),
                                    force_reload=force_reload, trust_repo=True)

    def run(self):
        # Run the Inference, draw predicted bboxes, and return people count
        results = self.model(self.img_path)
        df = results.pandas().xyxy[0]
        table_bboxes = []
        people_count = 0
        for _, row in df.iterrows():
            if row['class'] == 0 and row['confidence'] > self.conf:
                table_bboxes.append([int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])])
                people_count += 1

        img = cv2.imread(self.img_path)
        for i, table_bbox in enumerate(table_bboxes):
            label = f'Person {i}'
            plot_one_box(table_bbox, img, label=label, line_thickness=1)

        cv2.imwrite(os.path.join('src', 'output.png'), img)

        return people_count


def plot_one_box(x, img, color=None, label=None, line_thickness=3):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
