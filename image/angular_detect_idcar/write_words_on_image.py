#-*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import numpy as np
import random
import codecs
import pdb


def read_word(word_txt):
    f = codecs.open(word_txt, 'r','utf-8')
    lines = f.readlines()
    print len(lines)
    word_char=''
    for line in lines:
        line = line.strip('\n')
        line = line.replace('\t', '')
        line = line.replace('\r', '')
        line = line.replace(' ', '')
        word_char += line
    f.close()
    return word_char

def text_extract(words_set, item_num, length_limit, text_file_path):
    words_num = len(words_set)
    f = open(text_file_path, 'w')
    for i in range(item_num):
        #pdb.set_trace()
        item_list = []
        item_length = random.randint(0, length_limit)
        item_index = [random.randint(0, words_num-1) for i in range(item_length)]
        item_words = [words_set[index] for index in item_index]
        word_chars = ''.join(item_words)
        f.write(word_chars + '\n')
    f.close()

if __name__ == '__main__':
    word_chars_path = '/app/dev_user/yejinyu/detect_img/crnn/word_chars_5747.txt'
    fragment_save_path = '/app/dev_user/yejinyu/subtitle/corpus/uniform_picked_20w.txt'
    item_num = 200000
    length_limit = 25
    print 'Start...'
    word_chars = read_word(word_chars_path)
    print 'the words number is %d' %len(word_chars)
    text_extract(word_chars, item_num, length_limit, fragment_save_path)
    print 'Done...'
    


         
