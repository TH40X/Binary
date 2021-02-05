TIKTOK = False



ZOOM = 1.3

if TIKTOK:
    # usage for tiktik (vertical window)
    WINDOW_WIDTH = int(393 * ZOOM)
else:
    # usage for computer
    WINDOW_WIDTH = int(1200 * ZOOM)
WINDOW_HEIGHT = int(700 * ZOOM)


WINDOW_BG = "#303030"

INPUT_HEIGHT = 90
OUTPUT_HEIGHT = 50

DEBUG = 0
def debug(txt):
    if DEBUG:print(txt)

UPDATE_ID = 1
def PRE_UPDATE():
    global UPDATE_ID, UPDATE_NUMBER
    UPDATE_NUMBER = 0
    UPDATE_ID += 1

NODE_SIZE = 15

BOX_HEIGHT = 30
BOX_BG = "#bebebe"


NODE_NUMBER = 0
GATE_NUMBER = 0
UPDATE_NUMBER = 0
