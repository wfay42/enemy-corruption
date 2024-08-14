import subprocess
import glob
import json
import os
import shutil
import sys

PROCESSED_DIRNAME = 'processed'
COPY_FILENAME = 'copy.json'
CROPS_KEY = 'crops'
RESIZE_KEY = 'resize'

class CopyInstructions():
    def __init__(self, copy_instructions_json_file_path, copy_dirs_json_file_path):
        with open(copy_instructions_json_file_path) as fp:
            obj = json.load(fp)

        # all of these are lists
        self.skip = obj['skip']
        self.enemies = obj['enemies']
        self.faces = obj['faces']
        self.pictures = obj['pictures']
        self.titles = obj['titles']

        with open(copy_dirs_json_file_path) as fp:
            obj = json.load(fp)

        self.image_root_dir = obj['image_root_dir']

class DirCopyInstructions():
    """ Copy instructions for a single input image directory """
    def __init__(self, copy_instructions_json_file_path):
        with open(copy_instructions_json_file_path) as fp:
            obj = json.load(fp)

        self.default = obj['default']
        self.skip_list = obj['skip']
        self.custom = obj['custom']

class Converter():
    def __init__(self, convert_all = False):
        self.convert_all = convert_all

    def should_convert(self, img_path, out_img_path, skip_list = []):
        if self.convert_all:
            return True

        # if the name of the input file is in the list to skip
        if os.path.basename(img_path) in skip_list:
            return False

        # if the output file doesn't exist, we should make it
        if not os.path.exists(out_img_path):
            return True

        input_modify_time = os.path.getmtime(img_path)
        output_modify_time = os.path.getmtime(out_img_path)

        # if the input is newer than the output,
        # then the output is stale and we should update it
        return input_modify_time > output_modify_time

    def process_image(self, img_path, processed_dir, skip_list, crops, resize):
        """
        Crop and resize a single image, returning the subprocess that is asynchronously performing that change
        """
        filename = os.path.basename(img_path)
        out_img_path = os.path.join(processed_dir, filename)

        if not self.should_convert(img_path, out_img_path, skip_list):
            print("Skipping cropping %s to %s" % (img_path, out_img_path))
            return None

        arguments = ["magick", "convert"]
        for crop in crops:
            arguments.extend(['-crop', crop])
        arguments.extend(['-resize', resize])
        arguments.extend([img_path, out_img_path])

        print("Cropping: %s" % arguments)
        return subprocess.Popen(arguments)

    def copy_processed_files(self, input_processed_dir, output_dir):

        path_pattern = os.path.join(input_processed_dir, "*.png")
        path_list = glob.glob(path_pattern)

        for path in path_list:
            print("Copying %s into %s" % (path, output_dir))
            shutil.copy2(path, output_dir)

    def setup_output_dirs(self, input_dir_path):
        processed_dir = os.path.join(input_dir_path, PROCESSED_DIRNAME)
        if not os.path.exists(processed_dir):
            os.mkdir(processed_dir)
            print("Created dir for processed images: %s" % (processed_dir))
        return (processed_dir)

    def read_dir_copy_instructions(self, input_dir_path):
        copy_instructions_path = os.path.join(input_dir_path, COPY_FILENAME)
        dir_copy_instructions = DirCopyInstructions(copy_instructions_path)
        return dir_copy_instructions

    def get_crops_and_resizes(self, img_filename, dir_copy_instructions):
        default = dir_copy_instructions.default
        crops = default[CROPS_KEY]
        resize = default[RESIZE_KEY]

        custom = dir_copy_instructions.custom
        if img_filename in custom:
            crops, resize = custom[img_filename][CROPS_KEY], custom[img_filename][RESIZE_KEY]

        return crops, resize


    def process_images_for_directory(self, input_dir_path, output_dir_path):
        """
        Takes original (raw) images, and crops them appropriately
        """
        # create directories for processed images
        processed_dir = self.setup_output_dirs(input_dir_path)
        dir_copy_instructions = self.read_dir_copy_instructions(input_dir_path)
        default = dir_copy_instructions.default
        skip_list = dir_copy_instructions.skip_list

        # get input images
        path_pattern = os.path.join(input_dir_path, "*.png")
        path_list = glob.glob(path_pattern)

        conversion_popens = []
        for path in path_list:
            img_filename = os.path.basename(path)
            crops, resize = self.get_crops_and_resizes(img_filename, dir_copy_instructions)
            popen = self.process_image(path, processed_dir, skip_list, crops, resize)
            if popen is not None:
                conversion_popens.append(popen)

        # now that we kicked off all the conversions, check if they succeeded
        for popen in conversion_popens:
            success = popen.wait()
            print("Subprocess return code: %s" % success)

        self.copy_processed_files(processed_dir, output_dir_path)


    def process_all_directories(self, input_root_path, output_root_path, dir_list):
        for dir_name in dir_list:
            input_dir_path = os.path.join(input_root_path, dir_name)
            output_dir_path = os.path.join(output_root_path, dir_name)
            print("Will process %s and output to %s" % (input_dir_path, output_dir_path))
            self.process_images_for_directory(input_dir_path, output_dir_path)

def main():
    if len(sys.argv) < 4:
        print("Usage: convert.py input_directory copy_directory copy_instructions")
        return

    # eagerly initialize everything from arguments to find any issues
    root_path = sys.argv[1]
    copy_dirs_json_file_path = sys.argv[2]
    copy_instructions_json_file_path = sys.argv[3]
    copy_instructions = CopyInstructions(copy_instructions_json_file_path, copy_dirs_json_file_path)

    print("Converting files in directory %s" % root_path)
    converter = Converter()
    dir_list = ['enemies', 'faces', 'pictures']
    converter.process_all_directories(root_path, copy_instructions.image_root_dir, dir_list)

if __name__ == '__main__':
    main()
