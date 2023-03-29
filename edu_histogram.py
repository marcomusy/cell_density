"""EDU intensity"""
import sys
import numpy as np
import vedo
from vedo.pyplot import histogram, matrix

vedo.settings.use_parallel_projection = True
vedo.settings.remember_last_figure_format = True
vedo.settings.default_font = "Theemim"

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


def pick_threshold(event):
    global mat
    if event.actor and event.at == 2:
        threshold = event.picked3d[0]
        bin_data = (data > threshold).astype(np.int_)

        plt.at(1).remove(mat)
        mat = matrix(
            bin_data,
            cmap="Greys",
            title=f"Threshold = {threshold:.2f}",
            scale=0,  # size of bin labels; set it to 0 to remove labels
            lw=1,  # separator line width
        )
        plt.at(1).add(mat)
        arr = vedo.Arrow2D([threshold, 15], [threshold, 0]).z(1)
        plt.at(2).remove("Arrow2D").add(arr)
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
    label="data",
    aspect=1,
)
# print(hst.frequencies)

mat = matrix(
    data,
    cmap="Greys",
    title="Threshold: None",
    scale=0,  # size of bin labels; set it to 0 to remove labels
    lw=1,  # separator line width
)

# Plotting
plt = vedo.Plotter(N=3, sharecam=False)
plt.add_callback("on_click", pick_threshold)
plt.at(0).show(pic, zoom="tight")
plt.at(1).show(mat, zoom="tight")
plt.at(2).show(hst, zoom="tight", mode="image")
plt.interactive().close()
