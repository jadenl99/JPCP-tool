import os
import sys
import argparse



def get_im_id(s):
    s = s[::-1]
    start_index = -1 
    end_index = -1
    for i, c in enumerate(s):
        if c.isdigit():
            end_index = i + 1
            if start_index == -1:
                start_index = i
        elif start_index > -1:
            break

    if start_index == -1:
        return None

    return int(s[start_index:end_index][::-1])


def sort_by_num(l):
    l = sorted(l, key=lambda s: get_im_id(s))
    return l


def check_num(s1, s2):
    return get_im_id(s1) == get_im_id(s2)


def check_dir(dirname):

	"""
	Helper function to check the existence of range image and crack curve binary image
	directory

	"""

	if os.path.isdir(dirname) and os.path.exists(dirname):
		return True
	else:
		msg = "{0} is not a valid directory".format(dirname)
		raise argparse.ArgumentTypeError(msg)
