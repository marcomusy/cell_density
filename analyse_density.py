#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# USAGE:
# python analyse_density.py test_image.png
import sys
from vedo import settings
from vedo.pyplot import plot
from point_plotter import Plotter, PointPlotter

# Data ###################################
namein  = sys.argv[1]
nameout = namein.split('.')[-2]+"_data.csv"
radius = 50 # pixels

plt1 = PointPlotter(namein, nameout, init=nameout)
plt1.point_color = 'red5'
plt1.show(mode=7, zoom='tight').close()

# Analysis ################################
settings.enable_default_keyboard_callbacks = True
plt2 = Plotter(N=2, sharecam=False)
pts, dens, dens_array = plt1.compute_density(radius)
dens.pipeline.show()
intensities = plt1.get_intensities()
fig = plot(
    dens_array, intensities,
    lw=0,         # do not join points with lines
    xtitle=f"Density in radius {radius} (pixels)",
    ytitle="Sox9 intensity",
    marker="*",   # marker style
    mc="dr",      # marker color
)
plt2.at(0).show(pts, dens, plt1.pic.alpha(0.2), zoom='tight')
plt2.at(1).show(fig, zoom='tight')
plt2.screenshot(nameout.replace(".csv",".png"))
plt2.interactive().close()

