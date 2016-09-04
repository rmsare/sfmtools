""" Utility functions for PhotoScan processing """

import os, sys
import PhotoScan

def align_and_clean_photos(chunk):
    ncameras = len(chunk.cameras)
    chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.ReferencePreselection)
    chunk.alignCameras()
    
    for camera in chunk.cameras:
        if camera.transform is None:
            chunk.remove(camera)
    
    naligned = len(chunk.cameras)
    print('%d/%d cameras aligned' % (naligned, ncameras))

def export_dems(pathname, formatstring, resolution):
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
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
    
def export_orthos(pathname, resolution):
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    if pathname[-1:] is not '/':
        pathname = ''.join([pathname, '/'])
        
    nchunks = len(PhotoScan.app.document.chunks)
    nexported = nchunks
    for chunk in PhotoScan.app.document.chunks:
        filename = ''.join([pathname, ''.join(chunk.label.split(' ')), '.tif'])
        exported = chunk.exportOrthophotos(filename, raster_transform=PhotoScan.RasterTransformNone, write_kml=True, dx=resolution, dy=resolution, projection=chunk.crs)
        if not exported:
            print('Export failed:', chunk.label)
            nexported -= 1
    
    print('%d/%d Orthophotos exported' % (nexported, nchunks))
    
def filter_photos_by_quality(chunk, threshold):
    for camera in chunk.cameras:
        if camera.frames[0].photo.meta['Image/Quality'] is None:
            chunk.estimateImageQuality([camera])
        if float(camera.frames[0].photo.meta['Image/Quality']) < threshold:
            chunk.remove(camera)
  
def batch_process(projectname, threshold, resolution):
    doc = PhotoScan.app.document
    if projectname[-4:] is not '.psz':
        projectname = ''.join([projectname, '.psz'])
    if os.path.exists(projectname):
        doc.open(projectname)
        
    folders = ['dems', 'reports', 'orthos']
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)
    
    for chunk in doc.chunks:
        filter_photos_by_quality(chunk, threshold)
        align_and_clean_photos(chunk)
        chunk.buildDenseCloud(quality=PhotoScan.HighQuality)

    doc.alignChunks(doc.chunks, doc.chunks[0])
    doc.mergeChunks(doc.chunks, merge_dense_clouds=True, merge_markers=True)
    chunk = doc.chunks[len(doc.chunks)-1]
    chunk.buildModel(surface=Height, face_count=HighFaceCount)
    
    export_dems('dems/', 'tif', resolution)
    export_orthos('orthos/', resolution)
    
    for chunk in doc.chunks:
        filename = ''.join(['reports/', ''.join(chunk.label.split(' ')), '.pdf'])
        chunk.exportReport(filename)
        
    doc.save(projectname)
