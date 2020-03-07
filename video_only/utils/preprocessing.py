import cv2 as cv
import numpy as np
import torch
import os



def preprocess_sample(file, params):
    videoFile = file + ".mp4"
    roiFile = file + ".png"
    visualFeaturesFile = file + ".npy"

    roiSize = params["roiSize"]
    normMean = params["normMean"]
    normStd = params["normStd"]
    vf = params["vf"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    captureObj = cv.VideoCapture(videoFile)
    roiSequence = list()
    while (captureObj.isOpened()):
        ret, frame = captureObj.read()
        if ret == True:
            grayed = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            grayed = grayed/255
            grayed = cv.resize(grayed, (224,224))
            roi = grayed[int(112-(roiSize/2)):int(112+(roiSize/2)), int(112-(roiSize/2)):int(112+(roiSize/2))]
            roiSequence.append(roi)
        else:
            break
    captureObj.release()
    cv.imwrite(roiFile, np.floor(255*np.concatenate(roiSequence, axis=1)).astype(np.int))
    
    inp = np.stack(roiSequence, axis=0)
    inp = np.expand_dims(inp, axis=[1,2])
    inp = (inp - normMean)/normStd
    inputBatch = torch.from_numpy(inp)
    inputBatch = (inputBatch.float()).to(device)
    with torch.no_grad():
        outputBatch = vf(inputBatch)
    out = torch.squeeze(outputBatch, dim=1)
    out = out.cpu().numpy()
    np.save(visualFeaturesFile, out)
    return