import dm01
import sys
import os
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
example_dir_path = os.path.dirname(current_dir_path)
b_dir_path = os.path.join(example_dir_path, 'b')
sys.path.append(b_dir_path)
print('我不好')
import dm03