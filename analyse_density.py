#!/usr/bin/env python3
#
import sys
from vedo import settings, np
from vedo.pyplot import plot, fit
from point_plotter import Plotter, PointPlotter

# Data ###################################
namein  = sys.argv[1]
nameout = namein.replace('.tif','').replace('.png','') + "_data.csv"
radius = 100  # pixels

plt1 = PointPlotter(namein, nameout, init=nameout)
plt1.point_color = 'red5'
plt1.show(zoom='tightest', mode="image").close()

# Analysis ################################
settings.enable_default_keyboard_callbacks = True

pts, dens, dens_array = plt1.compute_density(radius)
intensities = plt1.get_intensities()
coeff = np.corrcoef(dens_array, intensities)[0][1]

fig = plot(
    dens_array, 
    intensities,
    title=f"Corr. coeff: {coeff: .3f}",
    xtitle=f"Density in {radius} pixels radius",
    ytitle="Sox9 intensity",
    lw=0,         # do not join points with lines
    marker="*",   # marker style
    mc="red4",    # marker color
    aspect=1/1,   # aspect ratio
)
fig += fit([dens_array, intensities])

plt2 = Plotter(N=2, sharecam=False)
plt2.at(0).show(namein, pts, dens, plt1.pic.alpha(0.2), zoom='tight')
plt2.at(1).show(fig, zoom='tight')
plt2.screenshot(nameout.replace("data.csv","screenshot.png"))
plt2.interactive().close()

