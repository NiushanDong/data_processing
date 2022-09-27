from base_py_func import *
import cv2
import numpy as np
import ipdb


def croped_img(img, lower_x, upper_x, lower_y, upper_y):
    w = img.shape[1]
    h = img.shape[0]
    # check inputs
    if w * h == 0:
        return None
    if lower_x < 0 or lower_x >= w or lower_y < 0 or lower_y >= h \
            or upper_x <= 0 or upper_x > w or upper_y <= 0 or upper_y > h:
        return None
    
    # crop
    return img[lower_y:upper_y, lower_x:upper_x, :]

def draw_points(img, points, size=5, color=None):
    all_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0)]
    for i, pt in enumerate(points):
        if color is None:
            color = (0, 0, 255) if img.shape[2] == 3 else 255
        color = all_colors[i % 4]
        cv2.circle(img, (pt[0], pt[1]), 5, color, -1)

def draw_polygon(img, points):
    points = np.array(points, np.int32)
    points = points.reshape((-1, 1, 2))
    cv2.polylines(img, [points], True, (0, 0, 255), 1)
    return img

def write_img(img_path, img):
    img_dir = os.path.dirname(img_path)
    try_make_dir(img_dir)
    cv2.imwrite(img_path, img)

def arrange_angular(src_points):
    all_x = [src_points[i][0] for i in range(len(src_points))]
    all_y = [src_points[i][1] for i in range(len(src_points))]
    all_x_sorted, idx_x = sort_list(all_x)

    # left points
    if all_y[idx_x[0]] <= all_y[idx_x[1]]:
        top_left = src_points[idx_x[0]]
        bottom_left = src_points[idx_x[1]]
    else:
        top_left = src_points[idx_x[1]]
        bottom_left = src_points[idx_x[0]]

    # right points
    if all_y[idx_x[2]] <= all_y[idx_x[3]]:
        top_right = src_points[idx_x[2]]
        bottom_right = src_points[idx_x[3]]
    else:
        top_right = src_points[idx_x[3]]
        bottom_right = src_points[idx_x[2]]

    return [top_left, top_right, bottom_left, bottom_right]

def rotate_img(src_img, angle, src_points=None):
    dst_img = src_img

    dst_points = None
    shape = src_img.shape
    h = shape[0]
    w = shape[1]
    c = shape[2]
    dst_size = int(pow(w*w+h*h, 0.5)) + 20
    
    # add cols and rows
    add_cols_oneside = int((dst_size - w) / 2)
    add_rows_oneside = int((dst_size - h) / 2)
    
    means = np.mean(src_img, axis=(0, 1)).astype(np.uint8)
    left = means * np.ones((h, add_cols_oneside, 3), dtype=np.uint8)
    right = means * np.ones((h, dst_size-add_cols_oneside-w, 3), dtype=np.uint8)
    top = means * np.ones((add_rows_oneside, dst_size, 3), dtype=np.uint8)
    bottom = means * np.ones((dst_size-add_rows_oneside-h, dst_size, 3), 
            dtype=np.uint8)
    dst_img = np.concatenate((left, dst_img), axis=1)
    dst_img = np.concatenate((dst_img, right), axis=1)
    dst_img = np.concatenate((top, dst_img), axis=0)
    dst_img = np.concatenate((dst_img, bottom), axis=0)

    # rotate
    M = cv2.getRotationMatrix2D((dst_size/2, dst_size/2), angle=angle, scale=1.0)
    dst_img = cv2.warpAffine(dst_img, M, (dst_size, dst_size), 
            borderValue=means.tolist())

    # calculate points
    pt_num = len(src_points)
    points = np.array(src_points, dtype=np.float32)
    points += np.array([add_cols_oneside, add_rows_oneside], dtype=np.float32)
    points = points.T

    points = np.concatenate((points, np.ones((1, pt_num), dtype=np.float32)), 
            axis=0)
    dst_points = np.dot(M, points).T.astype(int)
    dst_points = dst_points.tolist()

    return dst_img, dst_points


def rot90_anticlock(src_pts, img_size):
    ret = []
    w = img_size[0]
    for pt in src_pts:
        ret.append([pt[1], w-pt[0]-1])
    return ret


def rot90_clock(src_pts, img_size):
    ret = []
    h = img_size[1]
    for pt in src_pts:
        ret.append([h-pt[1]-1, pt[0]])
    return ret


def supplement_img(src_img, adds, src_points=None):
    dst_img = src_img

    dst_points = None
    shape = src_img.shape
    src_h = shape[0]
    src_w = shape[1]
    c = shape[2]

    # add cols and rows
    add_left = adds[0]
    add_right = adds[1]
    add_top = adds[2]
    add_bottom = adds[3]
    dst_h = src_h + add_top + add_bottom
    dst_w = src_w + add_left + add_right 

    means = np.mean(src_img, axis=(0, 1)).astype(np.uint8)
    left = means * np.ones((src_h, add_left, 3), dtype=np.uint8)
    right = means * np.ones((src_h, add_right, 3), dtype=np.uint8)
    top = means * np.ones((add_top, dst_w, 3), dtype=np.uint8)
    bottom = means * np.ones((add_bottom, dst_w, 3), dtype=np.uint8)
    dst_img = np.concatenate((left, dst_img), axis=1)
    dst_img = np.concatenate((dst_img, right), axis=1)
    dst_img = np.concatenate((top, dst_img), axis=0)
    dst_img = np.concatenate((dst_img, bottom), axis=0)
    
    dst_points = np.array(src_points, dtype=np.int32)
    dst_points += np.array([add_left, add_top], dtype=np.int32)
    dst_points = dst_points.tolist()

    return dst_img, dst_points

if __name__ == "__main__":
    img = cv2.imread("/app/dev_user/dataset/id_card/test/subset1_500/412725199012021533.jpg")
    #rotate_img(img, 45, src_points=[(28, 318), (12, 701), (648, 318), (649, 725)], 
    #        draw_pts=True)
    supplement_img(img, [30, 50, 90, 10], 
            src_points=[(28, 318), (12, 701), (648, 318), (649, 725)], 
            draw_pts=True)
