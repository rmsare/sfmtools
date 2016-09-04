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

def export_dems(pathname, formatstring, resolution):
    if not os.path.isdir(pathname):
        os.mkdir(pathname)
    if pathname[-1:] is not '/':
        pathname = ''.join([pathname, '/'])
        
    nchunks = len(PhotoScan.app.document.chunks)
    nexported = nchunks
    for chunk in PhotoScan.app.document.chunks:
        filename = ''.join([pathname, ''.join(chunk.label.split(' ')), '.', formatstring])
        exported = chunk.exportDem(filename, format=formatstring, dx=resolution, dy=resolution, projection=chunk.crs)
        if not exported:
            print('Export failed:', chunk.label)
            nexported -= 1
    
    print('%d/%d DEMs exported' % (nexported, nchunks))
    
def filter_photos_by_quality(chunk, threshold):
    for camera in chunk.cameras:
        if camera.frames[0].photo.meta['Image/Quality'] is None:
            chunk.estimateImageQuality([camera])
        if float(camera.frames[0].photo.meta['Image/Quality']) < threshold:
            chunk.remove(camera)
  
