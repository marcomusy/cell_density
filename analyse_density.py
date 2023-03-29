#!/usr/bin/env python3
#
import sys
from vedo import settings, np
from vedo.pyplot import plot, fit
from point_plotter import Plotter, PointPlotter

# Data ###################################
dapiin = sys.argv[1]
gfpin = sys.argv[2]
nameout = dapiin.replace(".tif", "").replace(".png", "") + "_data.csv"
radius = 100  # pixels

plt1 = PointPlotter(dapiin, gfpin, nameout, init=nameout)
plt1.point_color = "red5"
plt1.point_size = 8
plt1.show(zoom="tightest", mode="image").close()

# Analysis ################################
settings.enable_default_keyboard_callbacks = True

pts, dens, dens_array = plt1.compute_density(radius)
intensities = plt1.get_intensities()         # TODO get intensities of GFP
# intensities = np.random.rand(len(dens_array))  # TODO random values for now
coeff = np.corrcoef(dens_array, intensities)[0][1]

fig = plot(
    dens_array,
    intensities,
    title=f"Corr. coeff: {coeff: .3f} (n={len(dens_array)})",
    xtitle=f"Density in {radius} pixels radius",
    ytitle="Intensity",
    lw=0,          # do not join points with lines
    marker="*",    # marker style
    mc="red4",     # marker color
    aspect=1 / 1,  # aspect ratio
)

try:
    fig += fit([dens_array, intensities])
except ValueError as e:
    print(e)
    pass

plt2 = Plotter(N=2, sharecam=False)
plt2.at(0).show(dapiin[-30:], pts, dens, dens.box(), zoom=1.05)
plt2.at(1).show(fig, zoom="tight", mode="image")
plt2.screenshot(nameout.replace("data.csv", "screenshot.png"))
plt2.interactive().close()
