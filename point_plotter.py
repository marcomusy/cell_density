import numpy as np
from vedo import printc, settings, probe_points
from vedo import Plotter, Picture, Points, Text2D

settings.use_parallel_projection = True
settings.enable_default_keyboard_callbacks = False

txt = """Click to add a point
Right-click to remove it
Press w to write points
Press q to continue
Press a to toggle image"""
instructions = Text2D(
    txt, pos="bottom-left", font="Quikhand", c="white", bg="green4", alpha=0.75
)


#############################
class PointPlotter(Plotter):
    def __init__(self, filename, intfile, nameout, **kwargs):
        kwargs["title"] = "Cell Density Tool"
        kwargs["bg"] = "black"
        initfile = kwargs.pop("init", None)

        super().__init__(**kwargs)

        self.point_size = 8
        self.point_color = "red7"
        self.denfile = filename
        self.intfile = intfile
        self.nameout = nameout
        self.pic = Picture(filename).flip("y")  # .smooth(1)
        self.picgfp = Picture(intfile).flip("y").off()

        self.cpoints = []
        self.points = None
        if initfile is not None:
            try:
                self.cpoints = np.loadtxt(initfile, delimiter=",")[:, (0, 1)].tolist()
                self.points = (
                    Points(self.cpoints).ps(self.point_size).c(self.point_color)
                )
            except FileNotFoundError:
                printc("No init file", initfile, "continue.", c="y")

        tx = Text2D(self.denfile, font="Calco", s=0.9, bg="yellow3", alpha=0.75)
        self += [self.pic, self.picgfp, self.points, instructions, tx]

        self.add_callback("key press", self.on_key_press)
        self.add_callback("left mouse click", self.on_left_click)
        self.add_callback("right mouse click", self.on_right_click)

    def on_left_click(self, evt):
        if not evt.actor:
            return
        if evt.actor.name == "points":
            # remove clicked point if clicked twice
            pid = self.points.closest_point(evt.picked3d, return_point_id=True)
            self.cpoints.pop(pid)
            self.update()
            return
        self.cpoints.append(evt.picked3d[:2])
        self.update()
        # col = self.color_picker(evt.picked2d) # TODO get color of GFP

    def on_right_click(self, evt):
        if evt.actor and len(self.cpoints) > 0:
            self.cpoints.pop()  # pop removes from the list the last pt
            self.update()

    def on_key_press(self, evt):
        print(evt.keypress.lower())
        if "q" in evt.keypress.lower():
            out = np.round(self.cpoints).astype(int)
            # because one can forget to save the points
            np.savetxt("tmp_saved_coords.csv", out, fmt="%i", delimiter=",")
            self.close()
            return
        elif evt.keypress == "w":
            out = np.round(self.cpoints).astype(int)
            np.savetxt(self.nameout, out, fmt="%i", delimiter=",")
            printc(f"Saved {len(out)} cells in file {self.nameout}", c="b", invert=True)
        elif "a" in evt.keypress.lower():
            print("This should be working!")
            self.pic.toggle()
            self.picgfp.toggle()
            self.render()

    def update(self):
        self.remove(self.points)  # remove old points
        if len(self.cpoints):
            self.points = Points(np.array(self.cpoints)[:, (0, 1)])
            self.points.ps(self.point_size).c(self.point_color)
            self.points.name = "points"
            self.points.pickable(True)
            self.add(self.points)

    def get_coordinates(self):
        if len(self.cpoints) == 0:
            exit()
        return np.round(self.cpoints).astype(int)[:, (0, 1)]

    def get_intensities(self):  # TODO get intensities of GFP
        intensities = self.picgfp.tonumpy()
        coordinates = np.array(self.cpoints).astype(int)
        x, y = np.transpose(np.array(coordinates))
        return intensities[x, y]

    def compute_density(self, radius):
        cc = self.get_coordinates()
        pts = Points(cc)
        vol = pts.density(radius).c("YlOrRd").alpha(1)  # returns a Volume
        vol.add_scalarbar3d(title=f"Density (counts in r_search ={radius})", c="k")
        mpts = probe_points(vol, pts).ps(5).c("black")
        return mpts, vol, mpts.pointdata["ImageScalars"]
