import numpy as np
from vedo import printc, precision, settings, probe_points
from vedo import Plotter, Picture, Points, Text2D

settings.use_parallel_projection = True
settings.enable_default_keyboard_callbacks = False

txt = """Click to add a point
Right-click to remove it
Press c to clear points
Press w to write points"""
instructions = Text2D(
    txt, pos="bottom-left", font="Quikhand", c="white", bg="green4", alpha=0.5
)

#############################
class PointPlotter(Plotter):
    def __init__(self, filename, nameout, **kwargs):
        initfile = kwargs.pop("init", None)
        kwargs["bg"] = "black"
        super().__init__(**kwargs)

        self.point_size = 10
        self.point_color = "red8"
        self.filename = filename
        self.nameout = nameout
        self.pic = Picture(filename).bw()

        self.cpoints = []
        self.points = None
        if initfile is not None:
            try:
                self.cpoints = np.loadtxt(initfile, delimiter=",").tolist()
                self.points = Points(np.array(self.cpoints)[:, (0, 1)])
                self.points.ps(self.point_size).c(self.point_color)
            except FileNotFoundError:
                printc("No init file", initfile, "continue.", c="y")
        self += [self.pic, self.points, instructions, self.filename]

        self.add_callback("key press", self.on_key_press)
        self.add_callback("left mouse click", self.on_left_click)
        self.add_callback("right mouse click", self.on_right_click)

    def on_left_click(self, evt):
        col = self.color_picker(evt.picked2d)
        if not evt.actor:
            return
        if evt.actor.name == "points":
            # remove clicked point
            pid = self.points.closest_point(evt.picked3d, return_point_id=True)
            self.cpoints.pop(pid)
            self.update()
            printc("Deleted point id", pid, c="r")
            return
        p = evt.picked3d
        p = [p[0], p[1], np.mean(col)]
        self.cpoints.append(p)
        self.update()
        printc("Added point:", precision(p[:2], 4), col, c="g")

    def on_right_click(self, evt):
        if evt.actor and len(self.cpoints) > 0:
            self.cpoints.pop()  # pop removes from the list the last pt
            self.update()
            printc("Deleted last point", c="r")

    def on_key_press(self, evt):
        if "q" in evt.keypress.lower():
            out = np.round(self.cpoints).astype(int)
            np.savetxt(".tmp.csv", out, delimiter=",") # because one can forget to save
            self.close()
            return
        elif evt.keypress == "c":
            self.cpoints = []
            self.remove(self.points).render()
            printc("==== Cleared all points ====", c="r", invert=True)
        elif evt.keypress == "w":
            printc(f"==== Saved file {self.nameout} ====", c="b", invert=True)
            printc("   x   y   I    ", c="b", invert=True)
            out = np.round(self.cpoints).astype(int)
            printc(out, c="b")
            np.savetxt(self.nameout, out, delimiter=",")

    def update(self):
        self.remove(self.points)  # remove old points
        if len(self.cpoints):
            self.points = Points(np.array(self.cpoints)[:, (0, 1)])
            self.points.ps(self.point_size).c(self.point_color)
            self.points.name = "points"
            self.points.pickable(1)
            self.add(self.points)

    def get_coordinates(self):
        if len(self.cpoints) == 0:
            exit()
        return np.round(self.cpoints).astype(int)[:, (0, 1)]

    def get_intensities(self):
        return np.round(self.cpoints).astype(int)[:, 2]

    def compute_density(self, radius=None):
        cc = self.get_coordinates()
        pts = Points(cc)
        vol = pts.density(radius=radius).c("Paired_r")  # returns a Volume
        r = precision(vol.info["radius"], 2)  # retrieve radius value
        vol.add_scalarbar3d(title="Density (counts in r_search =" + r + ")", c="k")
        mpts = probe_points(vol, pts).point_size(3)  #.print()
        return pts, vol, mpts.pointdata["ImageScalars"]
