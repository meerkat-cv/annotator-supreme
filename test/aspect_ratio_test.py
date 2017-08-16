
import cv2

def set_aspect_ratio(image, aspect_ratio):
    if aspect_ratio.lower() == "4:3":
        ar = 4/3.;

    w = image.shape[1]
    h = image.shape[0]

    print("w",w,"h",h)
    if h < w:
        new_w = h*ar
        d_w = w - new_w
        
        start_x = int(d_w//2)
        end_x = int(w-(d_w//2))
        return image[:, start_x:end_x, :]
    else:
        new_h = w*ar
        d_h = h - new_h
        
        start_y = int(d_h//2)
        end_y = int(h-(d_h//2))
        return image[start_y:end_y, :, :]
        

img = cv2.imread("/Users/gfuhr/meerkat/datasets/cole_tv/brands/baycrest/102334946-09137fc0185a1e50185d6ec17d343044c414baf0.600x400.jpg")
cv2.imshow("original", img)

img_43 = set_aspect_ratio(img, "4:3")
cv2.imshow("ccw rotation", img_43)

cv2.waitKey(0)