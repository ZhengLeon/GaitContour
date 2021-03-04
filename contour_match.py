# meature two contours' simlarity, the lower score the better.
import cv2
import numpy as np
import matplotlib.pyplot as plt
img1 = cv2.imread('001-bg-01-000-001.png',0)
# img2 = cv2.imread('009-nm-01-036-001.png',0)
# img2 = cv2.imread('001-nm-01-000-001.png',0)
ret, thresh = cv2.threshold(img1, 127, 255,0)
# ret, thresh2 = cv2.threshold(img2, 127, 255,0)
contours,hierarchy = cv2.findContours(thresh,2,1)
cnt1 = contours[0]
x = []
y = []
for points in cnt1:
    x.append(points[0][0])
    y.append(128-points[0][1])
print(x)
# contours,hierarchy = cv2.findContours(thresh2,2,1)
# cnt2 = contours[0]
# ret = cv2.matchShapes(cnt1,cnt2,1,0.0)
# print(ret)
plt.axis([0,128,0,128])
plt.scatter(x, y, marker = 'x',color = 'red')
plt.show()  