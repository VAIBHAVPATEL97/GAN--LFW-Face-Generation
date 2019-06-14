#import cv2
#import matplotlib.pyplot as plt
#
#import numpy as np
#img = cv2.imread('1.png',1)
#plt.imshow(img)
import matplotlib.pyplot as plt
import cv2

def savegrid(ims, rows=None, cols=None, fill=True, showax=False):
    if rows is None != cols is None:
        raise ValueError("Set either both rows and cols or neither.")

    if rows is None:
        rows = len(ims)
        cols = 1

    gridspec_kw = {'wspace': 0, 'hspace': 0} if fill else {}
    fig,axarr = plt.subplots(rows, cols, gridspec_kw=gridspec_kw)

    if fill:
        bleed = 0
        fig.subplots_adjust(left=bleed, bottom=bleed, right=(1 - bleed), top=(1 - bleed))

    for ax,im in zip(axarr.ravel(), ims):
        ax.imshow(im)
        if not showax:
            ax.set_axis_off()

    kwargs = {'pad_inches': .01} if fill else {}
    i=fig.savefig('1.png', **kwargs)
    plt.imshow(i)