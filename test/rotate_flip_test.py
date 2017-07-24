
import cv2

img = cv2.imread("/Users/gfuhr/meerkat/datasets/cole_tv/brands/baycrest/102334946-09137fc0185a1e50185d6ec17d343044c414baf0.600x400.jpg")
cv2.imshow("original", img)

img_ccw = cv2.transpose(img)
img_ccw = cv2.flip(img_ccw, 0)
cv2.imshow("ccw rotation", img_ccw)

img_cw = cv2.flip(img, 0)
img_cw = cv2.transpose(img_cw)
cv2.imshow("cw rotation", img_cw)

img_v = cv2.flip(img, 0)
cv2.imshow("v flip", img_v)

img_h = cv2.flip(img, 1)
cv2.imshow("h flip", img_h)

cv2.waitKey(0)