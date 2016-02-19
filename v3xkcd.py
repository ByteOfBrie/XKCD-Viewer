'''
Drawille and curses xkcd reader
'''
import sys
import curses
import logging
from bs4 import BeautifulSoup
from drawille import Canvas
import requests
from io import BytesIO
from PIL import Image
import time

PAD_MOVE_X = 5
PAD_MOVE_Y = 5

def text_to_lines(hover_text, line_width):
    '''
    splits a string of words into individual lines
    '''
    hover_words = hover_text.split(' ')
    hover_lines = []
    line = ''
    for word in hover_words:
        if len(line) == 0:      #if the word is longer than the width it will do weird things
            line += word
        elif len(line) + len(word) + 1 <= line_width:
            line += ' '
            line += word
        else:
            hover_lines.append(line)
            line = word
    if line:
        hover_lines.append(line)
    return hover_lines

def calculate_screen_dims(screen_size, messages, lines):
    '''
    calculates and returns a tuple of the pad and the image width
    '''
    pad = [0, 0, 0, 0]          #top bottom left right
    img_dims = [0, 0]
    pad[2] = 5
    pad[3] = 5
    img_dims[1] = screen_size[1] - pad[2] - pad[3]
    pad[0] = 3 + len(messages) if messages else 4
    pad[1] = 2 + len(lines)
    img_dims[0] = screen_size[0] - pad[0] - pad[1]
    return pad, img_dims

def make_canvas(raw_img):
    '''
    use drawille functions to convert the image to text
    '''
    can = Canvas()
    img_bytes = raw_img.tobytes()
    place = [0, 0]

    for pix in img_bytes:
        if pix < 128:
            can.set(place[0], place[1])
        place[0] += 1
        if place[0] >= raw_img.size[0]:
            place[1] += 1
            place[0] = 0
    return can.frame()

def get_comic_img(comic_id, testing=False):
    '''
    gets the image, name, and hover text from xkcd.com for the number
    if testing is true it uses a saved comic (#1626)
    '''
    if testing:
        img = None
        with open('comicdata', 'r') as comicdata:
            img = comicdata.read().split('\n')
        title = 'Judgement Day'
        hover_text = ('It took a lot of booster rockets, but luckily Amazon had recently built '
                      'thousands of them to bring Amazon Prime '
                      'same-day delivery to the Moon colony.')
        return title, hover_text, img
    else:
        url = 'http://xkcd.com/{}/'.format(comic_id)
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        comic_data = soup.find(id='comic').contents[1]
        img_url = 'http:' + str(comic_data.get('src'))
        logging.debug('img url %s', img_url)
        title = comic_data.get('alt')
        hover_text = comic_data.get('title')
        pic_data = requests.get(img_url)
        raw_img = Image.open(BytesIO(pic_data.content))
        img = make_canvas(raw_img).split('\n')
        return title, hover_text, img

def parse_input(cmd, pad_offset, img_dims, img):
    '''
    handles all input
    '''

    message = None

    if cmd == 'KEY_DOWN':
        pad_offset[0] += PAD_MOVE_Y
        if pad_offset[0] + img_dims[0] >= len(img):
            message = 'Edge of image'
            pad_offset[0] = len(img) - img_dims[0]
            if pad_offset[0] < 0:
                pad_offset[0] = 0
    elif cmd == 'KEY_UP':
        pad_offset[0] -= PAD_MOVE_Y
        if pad_offset[0] <= 0:
            message = 'Edge of image'
            pad_offset[0] = 0
    elif cmd == 'KEY_RIGHT':
        pad_offset[1] += PAD_MOVE_X
        if pad_offset[1] + img_dims[1] >= len(img[0]):
            message = 'Edge of image'
            pad_offset[1] = len(img[0]) - img_dims[1]
            if pad_offset[1] < 0:
                pad_offset[1] = 0
    elif cmd == 'KEY_LEFT':
        pad_offset[1] -= PAD_MOVE_X
        if pad_offset[1] <= 0:
            message = 'Edge of image'
            pad_offset[1] = 0
    elif cmd == 'z':
        return None, None, -1
    elif cmd == 'c':
        return None, None, 1
    elif cmd == 'q':
        sys.exit(0)

    return pad_offset, message, None

def find_comic_ids(soup):
    '''
    get (prev, current, next) ids
    '''
    previd = int(soup.find(rel='prev').get('href')[1:-1])
    nextid = None
    try:
        nextid = soup.find(rel='next').get('href')[1:-1]
    except ValueError:
        pass
    currentid = list(soup.find('div', {'id':'middleContainer'}).children)[10][-5:-1]
    while currentid[0] not in '0123456789':
        currentid = currentid[1:]
    currentid = int(currentid)

    return previd, currentid, nextid


def main(stdscr):
    '''
    Curses fuction
    '''

    logging.basicConfig(filename='v3xkcd.log', level=logging.DEBUG)
    logging.debug('starting program')

    comic_id = 1626
    loaded = False

    while True:

        if not loaded:
            loaded = True
            stdscr.erase()
            stdscr.addstr(stdscr.getmaxyx()[0]//2, stdscr.getmaxyx()[1]//2 - 5, 'loading...')
            stdscr.refresh()
            title, hover_text, img = get_comic_img(comic_id, testing=True)

            pad_offset = [0, 0]
            messages = []

            pad, img_dims = calculate_screen_dims(stdscr.getmaxyx(), messages, [''])
            lines = text_to_lines(hover_text, img_dims[1])
            logging.debug(lines)

        pad, img_dims = calculate_screen_dims(stdscr.getmaxyx(), messages, lines)
        #if message is longer than screen width it will probably do weird things, not tested yet
        stdscr.erase()
        for i in range(img_dims[0]):
            if i + pad_offset[0] < len(img):
                j = img_dims[1] if img_dims[1] < len(img[0]) else len(img[0])
                stdscr.addstr(i + pad[0], pad[2],
                              img[i+pad_offset[0]][pad_offset[1] : pad_offset[1]+j])
        for i, line in enumerate(lines):
            stdscr.addstr(stdscr.getmaxyx()[0] - pad[1] + 1 + i, pad[2], line)
        stdscr.addstr(1, pad[2], 'Title: {}'.format(title))
        messages = list(item for item in messages if item)
        if messages:
            logging.debug(messages)
            for i, message in enumerate(messages):
                stdscr.addstr(2 + i, pad[2], message)
        cmd = stdscr.getkey()

        pad_offset, message, movement = parse_input(cmd, pad_offset, img_dims, img)
        if movement is None:
            messages = [message]
        else:
            comic_id += movement
            loaded = False

if __name__ == '__main__':
    curses.wrapper(main)
