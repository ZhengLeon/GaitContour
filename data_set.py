import torch.utils.data as tordata
import numpy as np
import os.path as osp
import os
import pickle
import cv2
import xarray as xr


class DataSet(tordata.Dataset):
    def __init__(self, seq_dir, label, seq_type, view, cache, resolution):
        self.seq_dir = seq_dir
        self.view = view
        self.seq_type = seq_type
        self.label = label
        self.cache = cache
        self.resolution = int(resolution)
        self.cut_padding = int(float(resolution)/64*10)
        self.data_size = len(self.label)
        self.data = [None] * self.data_size
        self.frame_set = [None] * self.data_size

        self.label_set = set(self.label)
        self.seq_type_set = set(self.seq_type)
        self.view_set = set(self.view)
        _ = np.zeros((len(self.label_set),
                      len(self.seq_type_set),
                      len(self.view_set))).astype('int')
        _ -= 1
        self.index_dict = xr.DataArray(
            _,
            coords={'label': sorted(list(self.label_set)),
                    'seq_type': sorted(list(self.seq_type_set)),
                    'view': sorted(list(self.view_set))},
            dims=['label', 'seq_type', 'view'])

        for i in range(self.data_size):
            _label = self.label[i]
            _seq_type = self.seq_type[i]
            _view = self.view[i]
            self.index_dict.loc[_label, _seq_type, _view] = i

    def load_all_data(self):
        for i in range(self.data_size):
            self.load_data(i)

    def load_data(self, index):
        return self.__getitem__(index)

    def __loader__(self, path):
        picture_seqs = self.img2xarray(
            path)[:, :, self.cut_padding:-self.cut_padding].astype(
            'float32') / 255.0
        # print(picture.shape)
        # print(type(picture_seqs[0]),picture_seqs[0].shape, picture_seqs[0])
        # ret, thresh = cv2.threshold(picture_seqs[0], 127, 255,0)
        # contours,hierarchy = cv2.findContours(thresh,2,1)
        # cnt1 = contours[0]
        # print(cnt1)
        return picture_seqs

    def __getitem__(self, index):
        # pose sequence sampling
        if not self.cache:
            data = [self.__loader__(_path) for _path in self.seq_dir[index]]
            frame_set = [set(feature.coords['frame'].values.tolist()) for feature in data]
            frame_set = list(set.intersection(*frame_set))
        elif self.data[index] is None:
            data = [self.__loader__(_path) for _path in self.seq_dir[index]]
            frame_set = [set(feature.coords['frame'].values.tolist()) for feature in data]
            frame_set = list(set.intersection(*frame_set))
            self.data[index] = data
            self.frame_set[index] = frame_set
        else:
            data = self.data[index]
            frame_set = self.frame_set[index]

        return data, frame_set, self.view[
            index], self.seq_type[index], self.label[index],

    def img2xarray(self, flie_path):
        imgs = sorted(list(os.listdir(flie_path)))
        frame_list = [np.reshape(
            # cv2.imread(osp.join(flie_path, _img_path)),
            self.get_contour(osp.join(flie_path, _img_path)),
            [self.resolution, self.resolution, -1])[:, :, 0]
                      for _img_path in imgs
                      if osp.isfile(osp.join(flie_path, _img_path))]
        num_list = list(range(len(frame_list)))
        data_dict = xr.DataArray(
            frame_list,
            coords={'frame': num_list},
            dims=['frame', 'img_y', 'img_x'],
        )
        return data_dict

    def __len__(self):
        return len(self.label)

    def get_contour(self,path):
        img1 = cv2.imread(path,0)
        # print(img1.shape)
        img_contour = np.zeros_like(img1)
        ret, thresh = cv2.threshold(img1, 127, 255,0)

        contours,hierarchy = cv2.findContours(thresh,2,1)
        # print(len(contours))
        # count = 0
        for cnt1 in contours:
            for i in range(len(cnt1)):
                point_h, point_w = cnt1[i][0][0], cnt1[i][0][1]
                img_contour[point_h][point_w] = 255#img1[point_h][point_w]
                # print(img1[point_h][point_w])
                # if img1[point_h][point_w] > 0:
                #     count = count + 1
        # print(count)
        return img_contour
