"""EDU intensity"""
import sys

import numpy as np
import vedo
from vedo.pyplot import histogram, matrix

vedo.settings.use_depth_peeling = True
vedo.settings.remember_last_figure_format = True


# Utils
def simple_mean_window_conv(data, r):
    """
    Simple convolution.
    Computes the value for each window, so that it reduces r times size.
    The Right and Bottom edges use as many cells as fit (< r)
    """
    n = np.ceil(data.shape[0] / r).astype(int)
    m = np.ceil(data.shape[1] / r).astype(int)
    w = np.zeros((n, m))

    for x, i in enumerate(np.arange(0, data.shape[0], r)):
        for y, j in enumerate(np.arange(0, data.shape[1], r)):
            window = data[i : i + r, j : j + r]
            w[x, y] = window.mean()

    return w


# Data
file = sys.argv[1]
radius = 25
pic = vedo.Picture(file)


# Reduce dimension of data

data = simple_mean_window_conv(pic.tonumpy(), radius)

# Histogram
hst = histogram(
    data.flatten(),
    # ylim=(0, 90),
    title=f"Intensity Window (r={radius})",
    xtitle="measured variable",
    c="red4",
    gap=0,  # no gap between bins
    padding=0,  # no extra spaces
    label="data",
    aspect=1
    # bins=100
)


def pick_treshold(event, data=data): 
    global mat
    if not event.actor:
        return

    treshold = event.picked3d[0]
    bin_data = (data > treshold).astype(np.int_)

    plt.at(1).clear().remove(mat)
    mat = matrix(
        bin_data,
        cmap="Greys",
        title=f"Treshold {treshold:.2f}",
        scale=0,  # size of bin labels; set it to 0 to remove labels
        lw=1,  # separator line width
    )
    plt.at(1).add(mat)
    plt.render()


# print(hst.frequencies)

# Matrix
mat = matrix(
    data,
    cmap="Greys",
    title="Treshold 0",
    scale=0,  # size of bin labels; set it to 0 to remove labels
    lw=1,  # separator line width
)

# Plotting
plt = vedo.Plotter(N=3, sharecam=False)
plt.at(0).show(pic, zoom="tight")
plt.at(1).show(mat, zoom="tight")
plt.at(2).show(hst, zoom="tight")
plt.add_callback("on_click", pick_treshold)
plt.interactive().close()
