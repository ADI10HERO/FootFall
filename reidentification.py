import tensorflow as tf
import numpy as np
import pybktree
import collections


db = collections.namedtuple('person', 'id-bits')
threshold = 2 # hyperparam
bktree = pybktree.BKTree(item_distance)


def item_distance(x, y):
    return pybktree.hamming_distance(x.bits, y.bits)


def dhash(img, size = 9):
    row_hash = 0
    col_hash = 0
    
    for x in range(size-1):
        for y in range(size-1):
            if img[x,y] < img[x,y+1]:
                row_hash = row_hash*10 + 1
            else:
                row_hash = row_hash*10 
            if img[y,x] < img[y,x+1]:
                col_hash = col_hash*10 + 1
            else:
                col_hash = col_hash*10 
    
    final_hash = int(str(row_hash) + str(col_hash)) 
    return final_hash


def reid(img, label):
    """
    img:
        target_size=(9, 9),
        color_mode="grayscale",
        batch_size=1
    label:
        temp_id
    """

    img = np.reshape(img, (9, 9))
    label = np.argmax(id)

    pred = sorted(bktree.find(db(id=label, bits=dhash(img)), threshold))[0][1].id
    if(pred == label):
        # TODO: What to do with permanent ids?
        print(pred, "is reid'ed correctly")
    else:
        # Adding new entry in db
        bktree.add(db(id=label, bits=dhash(img)))
    return pred # returning final ids?
