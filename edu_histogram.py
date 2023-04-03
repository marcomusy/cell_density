"""EDU intensity"""
import sys
import numpy as np
import vedo
from vedo.pyplot import histogram, matrix

vedo.settings.default_font = "Theemim"
vedo.settings.use_parallel_projection = True


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


def pick_threshold(event):
    if event.actor and event.at == 2:
        threshold = event.picked3d[0]
        bin_data = (data > threshold).astype(int)

        mat = matrix(
            bin_data,
            cmap="Greys",
            title=f"Threshold = {threshold:.2f}",
            scale=0,  # size of bin labels; set it to 0 to remove labels
            lw=1,     # separator line width
        )
        # trick to avoid a small vtk bug in visualization (thin diagonal line)
        mat.unpack(0).shrink(0.96).triangulate()

        arrow.on().x(threshold)  # show arrow at threshold value
        plt.at(1).remove("Matrix").add(mat)
        plt.render()


# Data
file = sys.argv[1]
radius = 25
pic = vedo.Picture(file)

# Reduce dimension of data
data = simple_mean_window_conv(pic.tonumpy(), radius)

# Histogram
hst = histogram(
    data.flatten(),
    xtitle=f"Intensity in r={radius} pixel window",
    c="red4",
    gap=0,  # no gap between bins
    aspect=1,
)
hst.verbose = False # avoid printing to stdout on every mouse click

mat = matrix(
    data,
    cmap="Greys",
    title="Threshold: None",
    scale=0,  # size of bin labels; set it to 0 to remove labels
    lw=1,     # separator line width
)
arrow = vedo.Arrow2D([0, 15], [0, 0]).z(1).off() # off initially

# Plotting
plt = vedo.Plotter(N=3, sharecam=False, title=file)
plt.add_callback("on_click", pick_threshold)
plt.at(0).show(pic, zoom="tight")
plt.at(1).show(mat, zoom="tightest")
plt.at(2).show(hst, arrow, zoom="tight", mode="image")
plt.interactive().close()
