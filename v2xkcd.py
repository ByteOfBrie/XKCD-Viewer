# -*- coding: utf-8 -*-
'''Simple XKCD terminal viewer'''

from PIL import Image
from io import BytesIO
import requests
from drawille import Canvas, getTerminalSize
from bs4 import BeautifulSoup
import curses
import time

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

def make_canvas(img):
    '''Make the image fit into the terminal'''
    desired = [225, 64]
    #desired[0] = int(img.size[0])
    #desired[1] = int(img.size[1])
    img = img.resize(desired, Image.ANTIALIAS)
    print('img', img.size)
    can = Canvas()
    place = [0, 0]

    try:
        img_converted = img.tobytes()
    except AttributeError:
        img_converted = img.tostring()

    for pix in img_converted:
        if pix < 128:
            can.set(place[0], place[1])
        place[0] += 1
        if place[0] >= img.size[0]:
            place[1] += 1
            place[0] = 0
    return can, desired

def scrollable(stdscr):
    pass
    #img, comic_name, extra_text = get_xkcd_data(1626)
    #can, size = make_canvas(img) #*****
    ##can = None
    ##with open('comicdata', 'r') as f:
    ##    can = f.read()
    #pad = curses.newpad(size[0], size[1])
    ##pad = curses.newpad(225, 64)
    #print(size)
    #time.sleep(5)
    #pad.addstr(can.frame())
    ##pad.addstr(can)
    #pad.refresh(0, 0, 0, 0, 50, 50)
    ##pad_coords = [0, 0]
    ##while True:
        #subpad = pad.subpad(70, 280, pad_coords[0], pad_coords[1])
        ##subpad = pad.subpad(30, 30, 5, 5)
        ##subpad.refresh(0, 0, 20, 0, 30, 30)
        ##cmd = subpad.getch()
        #print(cmd)
        ##if cmd == 66:
        ##    pad_coords[0] += 5
        ##elif cmd == 65:
        ##    pad_coords[0] -= 5
        ##elif cmd == 67:
        ##    pad_coords[1] += 5
        ##elif cmd == 68:
        ##    pad_coords[1] -= 5
        ##elif cmd == 113:
        ##    return

def main():
    img, comic_name, extra_text = get_xkcd_data(1626)
    #can = resize_img(img, (192, 200))
    print(getTerminalSize())
    print('title: ', comic_name)
    #print(can.frame())
    print('hover text: ', extra_text)

if __name__ == '__main__':
    main()
    #curses.wrapper(scrollable)
