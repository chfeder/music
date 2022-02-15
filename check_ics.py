#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2021

import numpy as np
import h5py
import argparse
import sys
import mytools as mt
from mytools import print, stop
import hdfio

def write_h5_dset(filename, dset_name, dset_data):
    outfilename = filename[:-5]+'_sorted_particles_by_x.hdf5'
    fout = None
    # if we write the x coordinate, then we overwrite the file (or create a new output file)
    if dset_name == "Baryons_x":
        fout = h5py.File(outfilename, 'w')
    else: # we append datasets
        fout = h5py.File(outfilename, 'a')
    fout.create_dataset(dset_name, data=dset_data)
    fout.close()
    print("Dataset '"+dset_name+"' in file '"+outfilename+"' written.")


# read HDF5 dataset from MUSIC output file; strip off buffer particles
def read_dset(filename, dsetn="DM_dx", level=7, buffer=4):
    level_str = "level_{:03d}".format(level) # construct level string
    datasetname = level_str+"_"+dsetn # construct HDF5 dataset name
    dat_gc = hdfio.read(filename, datasetname) # read from HDF5 file
    data = dat_gc[buffer:-buffer, buffer:-buffer, buffer:-buffer] # extract active particles; without buffers
    return data


# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Check FLASH initial conditions for baryons and dark matter particles from MUSIC.")
    parser.add_argument('-i', type=str, default="flash_music.hdf5", help="Input filename.")
    parser.add_argument('-buffer', type=int, default=4, help="Number of buffer particles.")
    parser.add_argument('-level', type=int, default=7, help="Level (powers of 2).")
    args = parser.parse_args()

    for parttype in ["DM", "BA"]:
        for plottype in ["pos", "vel", "rho", "pot"]:
            if plottype == "pos":
                if parttype == "DM": dsets = ["dx", "dy", "dz"]
                else: continue
            if plottype == "vel":
                dsets = ["vx", "vy", "vz"]
            if plottype == "rho":
                dsets = ["rho"]
            if plottype == "pot":
                if parttype == "DM": dsets = ["potential"]
                else: continue
            for dset in dsets:
                # read dataset
                dsetn = parttype+"_"+dset
                dat = read_dset(args.i, dsetn=dsetn, level=args.level, buffer=args.buffer)
                print("std("+dsetn+")="+str(np.std(dat)))
                # make a PDF
                pdf, x = mt.get_pdf(dat.flatten())
                mt.plot(x, pdf, label=mt.tex_escape(dset))
            mt.plot(xlabel=plottype, ylabel="PDF", save="PDF_"+parttype+"_"+plottype+"_l"+str(args.level)+".pdf")

    #stop()
