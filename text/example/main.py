import os
import sys

main_file_path = os.path.abspath(__file__)
example_dir_path = os.path.dirname(main_file_path)
b_dir_path = os.path.join(example_dir_path, 'b')
a_dir_path = os.path.join(example_dir_path, 'a')
sys.path.append(b_dir_path)
sys.path.append(a_dir_path)

import dm01
import dm02
import dm03