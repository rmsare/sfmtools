""" Utility functions for PhotoScan processing """

import os, sys
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

def export_dems(resolution, formatstring, pathname):
    if not os.path.isdir(pathname):
        os.mkdir(pathname)
    if pathname[-1:] is not '/':
        pathname = ''.join([pathname, '/'])
        
    nchunks = len(PhotoScan.app.document.chunks)
    nexported = nchunks
    for chunk in PhotoScan.app.document.chunks:
        filename = ''.join([pathname, ''.join(chunk.label.split(' ')), '.', formatstring])
        exported = chunk.exportDem(filename, format=formatstring, dx=resolution, dy=resolution)
        if not exported:
            print('Export failed:', chunk.label)
            nexported -= 1
    
    print('%d/%d DEMs exported' % (nexported, nchunks))
    
