'''
Drawille and curses xkcd reader
'''
import curses
import logging
from bs4 import BeautifulSoup
import time
from drawille import Canvas, getTerminalSize
import requests
from io import BytesIO
from PIL import Image

PAD_MOVE_X = 5
PAD_MOVE_Y = 5

def get_xkcd_data(comic_id):
    '''Grab the comic data and image based on the id'.'''
    url = 'http://xkcd.com/{}/'.format(comic_id)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

def text_to_lines(hover_text, line_width):
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
            line = ''
    return hover_lines

def main(stdscr):
    '''
    Curses fuction
    '''

    logging.basicConfig(filename='v3xkcd.log', level=logging.DEBUG)
    logging.debug('starting program')

    data = None
    with open('comicdata', 'r') as comicdata:
        data = comicdata.read().split('\n')
    title = 'Judgement Day'
    hover_text = ('It took a lot of booster rockets, but luckily Amazon had recently built '
                  'thousands of them to bring Amazon Prime same-day delivery to the Moon colony.')
    height, width = stdscr.getmaxyx()
    pad = [0, 0, 0, 0]
    pad_coords = [0, 0]
    img_dims = [0, 0]
    pad[2] = 5
    pad[3] = 5
    img_dims[0] = width - pad[2] - pad[3]
    lines = text_to_lines(hover_text, img_dims[0])
    pad[0] = 4
    pad[1] = 2 + len(lines)
    img_dims[1] = height - pad[0] - pad[1]
    messages = []
    while True:
        pad[0] = 4 if len(messages) == 0 else 3 + len(messages)
        pad[1] = 2 + len(lines)
        img_dims[1] = height - pad[0] - pad[1]
        #if message is longer than screen width it will do weird things, not tested yet
        stdscr.erase()
        for i in range(img_dims[1]):
            if i + pad_coords[0] < len(data):
                j = img_dims[0] if img_dims[0] < len(data[0]) else len(data[0])
                stdscr.addstr(i + pad[0], pad[2],
                              data[i+pad_coords[0]][pad_coords[1] : pad_coords[1]+j])
        stdscr.addstr(1, pad[2], 'Title: {}'.format(title))
        for i, message in iter(messages):
            stdscr.addstr(2 + i, pad[2], message)
        cmd = stdscr.getkey()
        logging.debug('cmd = %s', cmd)
        messages = []
        if cmd == 'KEY_DOWN':
            if pad_coords[0] + img_dims[1] >= len(data):
                messages.append('Edge of image')
                logging.debug('prevented scrolling at bottom of image')
            elif pad_coords[0] + img_dims[1] + PAD_MOVE_Y >= len(data):
                pad_coords[0] = len(data) - img_dims[1]
                if pad_coords[0] < 0:
                    pad_coords[0] = 0
            else:
                pad_coords[0] += PAD_MOVE_Y
                logging.debug('cmd += %g', PAD_MOVE_Y)
        elif cmd == 'KEY_UP':
            if pad_coords[0] <= 0:
                messages.append('Edge of image')
                logging.debug('prevented scrolling at top of image')
            elif pad_coords[0] - PAD_MOVE_Y <= 0:
                pad_coords[0] = 0
            else:
                pad_coords[0] -= PAD_MOVE_Y
                logging.debug('cmd -= %g', PAD_MOVE_Y)
        elif cmd == 'KEY_RIGHT':
            if pad_coords[1] + img_dims[0] >= len(data[0]):
                messages.append('Edge of image')
                logging.debug('prevented scrolling at side of image')
            elif pad_coords[1] + img_dims[0] + PAD_MOVE_X >= len(data[0]):
                pad_coords[1] = len(data[0]) - img_dims[0]
                if pad_coords[1] < 0:
                    pad_coords[1] = 0
            else:
                pad_coords[1] += PAD_MOVE_X
                logging.debug('pad[1] += %g', PAD_MOVE_X)
        elif cmd == 'KEY_LEFT':
            if pad_coords[1] <= 0:
                messages.append('Edge of image')
                logging.debug('prevented scrolling at top of image')
            elif pad_coords[1] - PAD_MOVE_X <= 0:
                pad_coords[1] = 0
            else:
                pad_coords[1] -= PAD_MOVE_X
                logging.debug('pad[1] -= %g', PAD_MOVE_X)
        elif cmd == 'q':
            return



if __name__ == '__main__':
    curses.wrapper(main)
