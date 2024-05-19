import subprocess
import glob
import json
import os
import shutil
import sys

class CopyInstructions():
    def __init__(self, copy_instructions_json_file_path, copy_dirs_json_file_path):
        with open(copy_instructions_json_file_path) as fp:
            obj = json.load(fp)

        # all of these are lists
        self.skip = obj['skip']
        self.enemies = obj['enemies']
        self.pictures = obj['pictures']
        self.titles = obj['titles']

        with open(copy_dirs_json_file_path) as fp:
            obj = json.load(fp)

        self.default_dir = obj['default_dir']
        self.enemies_dir = obj['enemies_dir']
        self.pictures_dir = obj['pictures_dir']
        self.titles_dir = obj['titles_dir']

class Converter():
    def __init__(self, convert_all = False):
        self.convert_all = convert_all

    def should_convert(self, img_path, out_img_path):
        if self.convert_all:
            return True

        # if the output file doesn't exist, we should make it
        if not os.path.exists(out_img_path):
            return True

        input_modify_time = os.path.getmtime(img_path)
        output_modify_time = os.path.getmtime(out_img_path)

        # if the input is newer than the output,
        # then the output is stale and we should update it
        return input_modify_time > output_modify_time

    def crop_image(self, img_path):
        """Crop a single image; skipping if not needed."""
        filename = os.path.basename(img_path)
        dirname = os.path.dirname(img_path)

        out_img_name = "_c-%s" % filename
        out_img_path = os.path.join(dirname, out_img_name)

        if not self.should_convert(img_path, out_img_path):
            print("Skipping cropping %s to %s" % (img_path, out_img_path))
            return None

        # TODO: should probably return a struct with the input and output paths
        return subprocess.Popen(["magick", "convert",
            "-crop", "+500+0+1000x1080",
            "-crop", "-520+0+1000x1080",
            img_path, out_img_path])

    def crop_original_images(self, root_path):
        """
        Takes original (raw) images, and crops them appropriately
        """
        path_pattern = os.path.join(root_path, "*.png")
        path_list = glob.glob(path_pattern)

        conversion_popens = []
        for path in path_list:
            # ignore cropped or resized images created from the conversion process
            basename = os.path.basename(path)
            if basename.startswith('_c') or basename.startswith('_r') or basename.startswith('ending'):
                continue
            popen = self.crop_image(path)
            if popen is not None:
                conversion_popens.append(popen)

        # now that we kicked off all the conversions, check if they succeeded
        for popen in conversion_popens:
            success = popen.wait()
            print("Subprocess return code: %s" % success)

    def resize_image(self, img_path):
        """
        Resize a specific image. Have pre-defined resolutions for enemies and endings.
        Everything else gets a different resolution
        """
        filename = os.path.basename(img_path)
        dirname = os.path.dirname(img_path)

        out_img_name = "_r%s" % filename
        out_img_path = os.path.join(dirname, out_img_name)

        if not self.should_convert(img_path, out_img_path):
            print("Skipping resizing %s to %s" % (img_path, out_img_path))
            return None

        # for a 1080 game, enemies can be 1080 if there are no character portraits
        dimensions = "1000x1080"
        if "enemy" in filename:
            dimensions = "1000x1080"
        # ending files we resize to the size of the game window
        elif "ending" in filename:
            dimensions = "1920x1080"

        # TODO: should probably return a struct with the input and output paths
        return subprocess.Popen(["magick", "convert",
            "-resize", dimensions,
            img_path, out_img_path])


    def resize_cropped_images(self, root_path):
        path_pattern = os.path.join(root_path, "_c*.png")
        path_list = glob.glob(path_pattern)

        path_pattern = os.path.join(root_path, "ending*.png")
        path_list.extend(glob.glob(path_pattern))

        conversion_popens = []
        for path in path_list:

            popen = self.resize_image(path)
            if popen is not None:
                conversion_popens.append(popen)

        # now that we kicked off all the conversions, check if they succeeded
        for popen in conversion_popens:
            success = popen.wait()
            print("Subprocess return code: %s" % success)

    def get_output_dir(self, basename, copy_instructions):
        output_dir = copy_instructions.default_dir
        if basename in copy_instructions.skip:
            output_dir = None
        elif basename in copy_instructions.enemies:
            output_dir = copy_instructions.enemies_dir
        elif basename in copy_instructions.pictures:
            output_dir = copy_instructions.pictures_dir
        elif basename in copy_instructions.titles:
            output_dir = copy_instructions.titles_dir

        return output_dir

    def copy_files(self, root_path, copy_instructions):
        path_pattern = os.path.join(root_path, "_r*.png")
        path_list = glob.glob(path_pattern)
        print(path_list)

        for path in path_list:
            basename = os.path.basename(path)

            output_dir = self.get_output_dir(basename, copy_instructions)
            if output_dir is None:
                print("Skipping copying %s because it is in the skip list" % path)
                continue

            # output file name should remove the _r_c cruft for resized/cropped
            new_name = basename.replace("_r", "").replace("_c-", "")

            # if we know this file name should be copied and to where,
            # let's see if it's up to date and doesn't need to be copied
            output_path = os.path.join(output_dir, new_name)
            if not self.should_convert(path, output_path):
                print("Skipping copying %s to %s" % (path, output_path))
                continue

            print("Copying %s to %s" % (path, output_path))
            shutil.copy2(path, output_path)

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
    converter.crop_original_images(root_path)
    print("Cropping complete.  Starting resizing.")
    converter.resize_cropped_images(root_path)

    # copy the resized files somewhere
    converter.copy_files(root_path, copy_instructions)

if __name__ == '__main__':
    main()
