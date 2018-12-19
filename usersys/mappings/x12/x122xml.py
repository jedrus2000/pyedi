# mapping-script for xmlnocheck
import copy

def main(inn,out):
    out.root = copy.deepcopy(inn.root)
