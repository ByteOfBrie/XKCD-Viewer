# -*- coding: utf-8 -*-
'''Simple XKCD terminal viewer'''

from PIL import Image
from io import BytesIO
import requests
from drawille import Canvas, getTerminalSize
from bs4 import BeautifulSoup

def get_xkcd_data(comic_id):
    '''Grab the comic data and image based on the id.'''
    url = 'http://xkcd.com/%s/' % comic_id
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    comic_data = soup.find(id='comic').contents[1]
    img_url = 'http:' + str(comic_data.get('src'))
    comic_name = comic_data.get('alt')
    extra_text = comic_data.get('title')
    pic_data = requests.get(img_url)
    img = Image.open(BytesIO(pic_data.content))
    return img, comic_name, extra_text

def resize_img(img, desired):
    '''Make the image fit into the terminal'''
    if desired[0] < img.size[0]:
        #ratio = desired[1] / float(img.size[1])
        #print(ratio)
        #new_height = int(img.size[1]*ratio)
        #print(desired, new_height)
        #img = img.resize(desired, Image.ANTIALIAS)
        print('img', img.size)
    can = Canvas()
    x = y = 0

    try:
        img_converted = img.tobytes()
    except AttributeError:
        img_converted = img.tostring()

    for pix in img_converted:
        if pix < 128:
            can.set(x, y)
        x += 1
        if x >= img.size[0]:
            y += 1
            x = 0
    return can

def main():
    img, comic_name, extra_text = get_xkcd_data(1626)
    can = resize_img(img, (46*5, 168*5))
    print(getTerminalSize())
    print('title: ', comic_name)
    print(can.frame())
    with open('comicdata', 'w') as f:
        f.write(can.frame())
    print('hover text: ', extra_text)

if __name__ == '__main__':
    main()
