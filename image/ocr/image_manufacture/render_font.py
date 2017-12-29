mport random
import numpy as np
import cv2
from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

font_list = [
        './gen_data/fonts/华文中宋.ttf',
        './gen_data/fonts[表情]shi.ttf']


def border(alpha, size, kernel_type='RECT'):
        k_dict = {
                'RECT': cv2.MORPH_RECT,
                'ELLIPSE': cv2.MORPH_ELLIPSE,
                'CROSS': cv2.MORPH_CROSS}
        kernel = cv2.getStructuringElement(k_dict[kernel_type], (size, size))
    _border = cv2.dilate(alpha, kernel, iterations=1)  # - alpha
    return _border


def draw_dash(image):
    '''在图像的alpha通道上画虚线
    距离文字下方画虚线，一定的概率不画，一定的概率在上中下部分画'''
    distance = random.uniform(-0.5, 3.5)
    h, w, c = image.shape
    # 虚线在文字上方
    if distance < 0.0:
        distance = np.abs(distance)
        expand_h = int(h * distance)
        big_h = h + expand_h
        big_image = np.zeros((big_h, w, c), dtype=np.uint8)
        big_image[expand_h:, :, :] = image
        for c in range(0, w, 12):
            cv2.line(big_image, (c, 1), (c + 4, 1), (0, 0, 0, 255), 2)

    # 虚线在文字高度内部
    elif distance >= 0.0 and distance <= 1.0:
        line_h = int(h * distance)
        big_image = image
        for c in range(0, w, 12):
            cv2.line(big_image, (c, line_h), (c + 4, line_h), (0, 0, 0, 255), 2)

    # 虚线在文字下方
    elif distance > 1.0 and distance < 1.5:
        distance = distance - 1.0
        expand_h = int(h * distance)
        big_h = h + expand_h
        big_image = np.zeros((big_h, w, c), dtype=np.uint8)
        big_image[:h, :, :] = image
        for c in range(0, w, 12):
            cv2.line(big_image, (c, big_h - 2), (c + 4, big_h - 2), (0, 0, 0, 255), 2)
    else:
        return image

    return big_image


def render_font(word_list, size, gap, resize_factor):
    image = Image.new('RGBA', (100, 100), color=(0, 0, 0, 0))
    draw = Draw(image)

    def _draw_character(c):
        if c == 'W':
            img = cv2.imread('W_C.jpg', 0)
            h, w = img.shape[:2]
            zero_img = np.zeros((h, w, 4), dtype=np.uint8)
            zero_img[:, :, 3] = img
            im = Image.fromarray(zero_img)
            return im
        if c in '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            font_id = 1
        else:
            font_id = 0
        _font = truetype(font_list[font_id], size)
        rotated = False
        if c == 'M':
            c = 'W'
            rotated = True
        w, h = draw.textsize(c, font=_font)
        im = Image.new('RGBA', (w, h))
        Draw(im).text((0, 0), c, font=_font, fill=(0, 0, 0, 255))
        im = im.crop(im.getbbox())
        if rotated:
            im = im.rotate(180)
        return im

    images = []
    for c in word_list:
        char_img = _draw_character(c)
        images.append(char_img)

    text_width = sum([im.width for im in images])
    text_height = max([im.height for im in images])

    image = image.resize((text_width * 3, text_height))
    average = int(text_width / len(word_list))
    # 左边加一段空白
    left_gap = min(5, len(word_list))
    offset = int(random.uniform(0.0, gap * left_gap) * average)

    for idx, im in enumerate(images):
        factor = random.uniform(resize_factor, 1.0)
        w, h = im.size
        im = im.resize((int(w * factor), int(h * factor)))
        w, h = im.size
        up_line = random.randint(
                int((text_height - h) * 0.2), 
                int((text_height - h) * 0.8))
                image.paste(im, (offset, up_line))
        # 当前字符或者下一个字符是'-'
        if word_list[idx] == '-' \
                or (idx < len(word_list) - 1 and word_list[idx + 1] == '-'):
            offset += w + int(random.uniform(0.0, gap) * average * 0.25)
        else:
            offset += w + int(random.uniform(0.0, gap) * average)

    right_gap = left_gap - 1
    offset += int(random.uniform(0.0, gap * right_gap) * average)
    image = image.crop((0, 0, offset, text_height))
    image = draw_dash(np.array(image))

    return image
