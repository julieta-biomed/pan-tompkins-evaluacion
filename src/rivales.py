import numpy as np
from scipy import signal as sg
from pantom import cadena

def ingenuo(x, fs, k=0.6):
    """Detector ingenuo: umbral fijo sobre la senal cruda."""
    p,_ = sg.find_peaks(x, height=k*np.max(x), distance=int(0.25*fs))
    return p/fs

def umbral_fijo(x, fs, k=0.25, ventana=0.150):
    """Cadena de Pan-Tompkins + umbral fijo, sin heuristicas."""
    _,_,_,i = cadena(x, fs, ventana=ventana)
    p,_ = sg.find_peaks(i, height=k*np.percentile(i,99), distance=int(0.25*fs))
    return p/fs
