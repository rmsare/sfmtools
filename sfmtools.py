""" Utility functions for PhotoScan processing """

import os
import PhotoScan

def align_and_clean_photos(chunk):
    ncameras = len(chunk.cameras)
    for frame in chunk.frames:
        frame.matchPhotos()

    chunk.alignCameras()
    for camera in chunk.cameras:
        if camera.transform is None:
            chunk.remove(camera)
    
    naligned = len(chunk.cameras)
    print('%d/%d cameras aligned' % (naligned, ncameras))


    
