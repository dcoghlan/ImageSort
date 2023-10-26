# Script to read exif information from a file and move it to a destination folder
# based on the date contained within the EXIF data

# for testing, to roll back, can use the following bash cmd
# for x in $(find . -type f | grep -v DS_Store); do mv $x ~/Pictures/tosort/; done
# for x in $(find . -type f | grep -v DS_Store); do mv $x ~/Pictures/iphone_xs_max/; done

# To sync the output folders to the NAS, use the following shell cmd
# cd /Users/dcoghlan/Desktop/tocopy/
# for n in $(ls -l | grep ^d | awk '{print $9}'); do rsync --exclude=.DS_Store -avz /Users/dcoghlan/Desktop/tocopy/$n/ /Volumes/data-1/Pictures/$n/; done

import glob
# from exif import Image
import exif
import os
from datetime import datetime
import glog as log
import shutil
import pytz
import argparse
import exifread

_SRC_DIR = "/Users/dcoghlan/Pictures/iphone_xs_max/"
# _SRC_DIR = "/Users/dcoghlan/Pictures/iphone_xs_max/dev"
# _SRC_DIR = "/Users/dcoghlan/Pictures/tosort/"
_DST_ROOT = "/Users/dcoghlan/Desktop/tocopy/"
_timezone = "Australia/Sydney"

  
_SKIP_FILE_TYPES = [".MOV", ".AAE", ".MP4"]

_IMAGE_FILE_EXTS = ["JPG", "JPEG", "PNG", "AAE", "WEBP", "GIF", "TIFF"]
_VIDEO_FILE_EXTS = ["MOV", "MP4", "M4V"]
_MISC_FILE_EXTS = ["PDF"]
_APPLE_IMAGE_FILE_EXTS = ["HEIC"]

# def main():
#     """Main script function"""
#     # get list of files
#     # remove/ignore file types specified in _SKIP_FILE_TYPES
#     # try and load image via Image class

# if __name__ == "__main__":
#     main()
class ImageSorta():
    """ This is the docstring
    """

    def __init__(self, args, path, tz, IMAGE_FILE_EXTS, VIDEO_FILE_EXTS, MISC_FILE_EXTS, APPLE_IMAGE_FILE_EXTS, DST_ROOT ):
        self.args = args
        self.path = path
        self.filename = os.path.basename(self.path)
        self.fileext = os.path.splitext(self.filename)[1].lstrip('.')
        self.tz = tz
        self.IMAGE_FILE_EXTS = IMAGE_FILE_EXTS
        self.VIDEO_FILE_EXTS = VIDEO_FILE_EXTS
        self.MISC_FILE_EXTS = MISC_FILE_EXTS
        self.APPLE_IMAGE_FILE_EXTS = APPLE_IMAGE_FILE_EXTS
        self.DST_ROOT = DST_ROOT
        self.filetype = None
        self.datetime = None
    
    def get_filename(self):
        return self.filename
    
    def get_fileext(self):
        return self.filetype.upper()

    def _get_image_date(self):
        log.debug(f"[{self.filename}] Trying to determine image date")

        try:
            image_obj = exif.Image(self.path)
        except Exception as e:
            if self.args.loglevel.upper() == "DEBUG":
                log.error(f"[{self.filename}] Not an image file, defaulting to creation/modified dates")
                log.error(f"{e}")
            self._get_file_date()
            return

        self._get_exif_date(image_obj)

    def _extract_heic_datetime(self):
        """Extracts the datetime from a HEIC file.

        Args:
            heic_file_path: The path to the HEIC file.

        Returns:
            A datetime object representing the datetime the HEIC file was taken.
        """

        # Open image file for reading (must be in binary mode)
        with open(self.path, "rb") as file_handle:

            # Return Exif tags
            tags = exifread.process_file(file_handle, details=False, stop_tag='DateTimeOriginal')

            if tags.get("datetime_original"):
                self.datetime = datetime.strptime(str(tags.get('EXIF DateTimeOriginal')), '%Y:%m:%d %H:%M:%S')
            else:
                if self.args.loglevel.upper() == "DEBUG":
                    log.warn(f"[{self.filename}] Unable to find any datetime fields in EXIF, defaulting to creation/modified dates")
                self._get_file_date()

    def _get_file_date(self):
        log.debug(f"[{self.filename}] Trying to determine file date")
        # Get file metadata
        file_stat = os.stat(self.path)

        # Extract the creation (birth) time and modification time (in epoch format)
        creation_timestamp = file_stat.st_birthtime
        modification_timestamp = file_stat.st_mtime

        # Specify the target time zone (UTC+10)
        target_timezone = pytz.timezone(self.tz)

        # Convert epoch timestamps to the target time zone
        creation_time_tz_aware = datetime.fromtimestamp(creation_timestamp, target_timezone)
        modification_time_tz_aware = datetime.fromtimestamp(modification_timestamp, target_timezone)

        log.debug(f"[{self.filename}] Creation Time ({self.tz}): {creation_time_tz_aware}")
        log.debug(f"[{self.filename}] Modification Time ({self.tz}): {modification_time_tz_aware}")

        # Compare the creation and modification times
        if creation_time_tz_aware < modification_time_tz_aware:
            log.debug(f"[{self.filename}] Creation time is earlier.")
            self.datetime = creation_time_tz_aware
        elif creation_time_tz_aware > modification_time_tz_aware:
            log.debug(f"[{self.filename}] Modification time is earlier.")
            self.datetime = modification_time_tz_aware
        else:
            log.debug(f"[{self.filename}] Creation and modification times are the same.")
            self.datetime = creation_time_tz_aware

    def _get_exif_date(self, image):
        log.debug(f"[{self.filename}] Trying to get date from exif")

        if image.has_exif:
            # status = f"contains EXIF (version {image_file.exif_version}) information."
            # print(f"Image {file} {status}")
            # print(dir(image_file))
            # if "datetime_original" in image_file:
            if image.get("datetime_original"):
                self.datetime = datetime.strptime(image['datetime_original'], '%Y:%m:%d %H:%M:%S')
            # elif "datetime_digitized" in image_file:
            elif image.get("datetime_digitized"):
                self.datetime = datetime.strptime(image['datetime_digitized'], '%Y:%m:%d %H:%M:%S')
            elif image.get("datetime"):
                self.datetime = datetime.strptime(image['datetime'], '%Y:%m:%d %H:%M:%S')
            else:
                if self.args.loglevel.upper() == "DEBUG":
                    log.warn(f"[{self.filename}] Unable to find any datetime fields in EXIF, defaulting to creation/modified dates")
                    log.error(f"{image.get_all()}")
                    log.error(f"{dir(image)}")
                self._get_file_date()
        else:
            if self.args.loglevel.upper() == "DEBUG":
                log.warn(f"[{self.filename}] does not contain any EXIF information.")
            self._get_file_date()
            # return None

    def _move_file(self):

        year = datetime.strftime(self.datetime, '%Y' )
        newdirname = datetime.strftime(self.datetime, '%Y%m%d' )
        # print(folder_name)
        dst_folder = os.path.join(self.DST_ROOT ,year, newdirname)
        dst_full_path = os.path.join(dst_folder ,self.filename)
        if not os.path.isdir(dst_folder):
            log.info(f"[{self.filename}] Creating folder: {dst_folder}")
            os.makedirs(dst_folder)
        log.info(f"[{self.filename}] moving: {self.path} > {dst_full_path}")
        shutil.move(self.path, dst_full_path)
        # exit()


    def process_file(self):
        """run the actual process
        - figure out what type of file it is
        """
        if self.fileext.upper() in self.APPLE_IMAGE_FILE_EXTS:
            self.filetype = "apple-image"
            log.debug(f"[{self.filename}] Filetype = {self.filetype}")
            self._extract_heic_datetime()
        elif self.fileext.upper() in self.IMAGE_FILE_EXTS:
            self.filetype = "image"
            log.debug(f"[{self.filename}] Filetype = {self.filetype}")
            self._get_image_date()
        elif self.fileext.upper() in self.VIDEO_FILE_EXTS:
            self.filetype = "video"
            log.debug(f"[{self.filename}] Filetype = {self.filetype}")
            self._get_file_date()
        elif self.fileext.upper() in self.MISC_FILE_EXTS:
            self.filetype = "misc"
            log.debug(f"[{self.filename}] Filetype = {self.filetype}")
            self._get_file_date()
        else:
            log.error(f"[{self.filename}] Unknown file extension: {self.fileext.upper()}")

        log.debug(f"[{self.filename}] datetime = {self.datetime}")
        
        if self.datetime is not None:
            self._move_file()
        else:
            log.warn(f"[{self.filename}] Unable to move file as no datetime information can be found")

def parse_args():
    """Command line argument parser"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Path to file or folder",
    )
    parser.add_argument(
        "--loglevel",
        type=str,
        nargs="?",
        default="INFO",
        const="INFO",
        help="Specify logging level. Default is INFO.",
    )

    args = parser.parse_args()
    
    return args

def main():
    args = parse_args()
    log.setLevel(args.loglevel.upper())

    for item in sorted(glob.glob(os.path.join(_SRC_DIR, '*'))):
        if os.path.isfile(item):
            log.debug("processing file: %s" %(item))
            imagesorta = ImageSorta(args, item, _timezone, _IMAGE_FILE_EXTS, _VIDEO_FILE_EXTS, _MISC_FILE_EXTS, _APPLE_IMAGE_FILE_EXTS, _DST_ROOT)
            imagesorta.process_file()

if __name__ == "__main__":
    main()
