import sys
import os

conf_path = os.path.abspath(__file__)
dirpath_of_conf = os.path.dirname(conf_path)
src_dir_path = os.path.abspath(dirpath_of_conf + '/../src/')
sys.path.append(src_dir_path)
