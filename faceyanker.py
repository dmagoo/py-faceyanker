import os,platform
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.ttk import Treeview

import numpy as np
from stl import mesh
import svgwrite

from meshloader import *
from scene import Scene, SceneViewer, \
    SCENE_PERSPECTIVE_FRONT, \
    SCENE_PERSPECTIVE_TOP, \
    SCENE_PERSPECTIVE_LEFT, \
    SCENE_PERSPECTIVE_RIGHT, \
    SCENE_PERSPECTIVE_BOTTOM, \
    SCENE_PERSPECTIVE_BACK

DEFAULT_MODEL_CANVAS_DIMENSIONS = (600,600)
DEBUG = False

class FaceYankerApp:
    def __init__(self,master, test=False):
        self.root = master
        self.model_screen = None
        self.init_ui()
        self.embed_sdl()
        self.scene = Scene()
        self.scene_viewer = SceneViewer(self.scene,DEFAULT_MODEL_CANVAS_DIMENSIONS)
        if test:
            self.test()
        else:
            self.root.mainloop()

        try:
            self.root.destroy()
        except:
            pass

    def init_ui(self):
        frame = Frame(self.root)
        frame.pack()
        frame.bind("<KeyPress>", self.keydown)
        frame.focus_set()

        self.init_menu(frame)
        self.init_canvas()
        self.model_explorer = self.init_model_explorer()

    def init_menu(self,frame):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Import Model", command=self.on_open, accelerator="Ctrl+O", underline=0)
        fileMenu.add_command(label="Export SVG", command=self.on_export, accelerator="Ctrl+S", underline=0)
        fileMenu.add_command(label="Exit", command=frame.quit, accelerator="Ctrl+X", underline=1)
        menubar.add_cascade(label="File", menu=fileMenu, underline=0)

        modelMenu = Menu(menubar)
        modelMenu.add_command(label="Reduce Model", command=self.on_flatten_model, underline=0)
        menubar.add_cascade(label="Model", menu=modelMenu, underline=0)

        viewMenu = Menu(menubar)
        viewMenu.add_command(label="Toggle Normals", underline=7, command=self.on_toggle_normals)
        viewMenu.add_command(label="Toggle Grid", underline=7, command=self.on_toggle_grid)
        viewMenu.add_command(label="Toggle Model Tree", underline=7, command=self.on_toggle_model_explorer)
        viewMenu.add_separator()
        viewMenu.add_command(label="Front View", underline=0, command=lambda:self.on_set_perspective(SCENE_PERSPECTIVE_FRONT))
        viewMenu.add_command(label="Top View", underline=0, command=lambda:self.on_set_perspective(SCENE_PERSPECTIVE_TOP))
        viewMenu.add_command(label="Left View", underline=0, command=lambda:self.on_set_perspective(SCENE_PERSPECTIVE_LEFT))
        viewMenu.add_command(label="Right View", underline=0, command=lambda:self.on_set_perspective(SCENE_PERSPECTIVE_RIGHT))
        viewMenu.add_command(label="Back View", underline=0, command=lambda:self.on_set_perspective(SCENE_PERSPECTIVE_BACK))
        viewMenu.add_command(label="Bottom View", underline=1, command=lambda:self.on_set_perspective(SCENE_PERSPECTIVE_BOTTOM))

        menubar.add_cascade(label="View", menu=viewMenu, underline=0)

    def init_canvas(self):
        """ reserved for non pygame canvas stuff (placeholder) """
        w = Canvas(self.root, width=300, height=450)
        w.pack(side="right",fill="both")

    def embed_sdl(self):
        embed = Frame(self.root, width = DEFAULT_MODEL_CANVAS_DIMENSIONS[0], height = DEFAULT_MODEL_CANVAS_DIMENSIONS[1]) #creates embed frame for pygame window
        #embed.grid(columnspan = (600), rowspan = 500) # Adds grid
        embed.pack(side = LEFT) #packs window to the left
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'

    def init_model_explorer(self):
        tree = ttk.Treeview(self.root,columns=("normal"), displaycolumns="normal", height=35)
        tree.column("normal", width=75)
        tree.heading("normal", text="Normal")
        tree.tag_bind("face","<<TreeviewSelect>>", self.on_face_select)
        my_scroll = ttk.Scrollbar(orient="vertical")
        my_scroll.configure(command=tree.yview)
        tree.configure(yscrollcommand=my_scroll)
        tree.pack(side=LEFT, fill="y")
        my_scroll.pack(side=LEFT, fill="y", expand=False)#grid(row=1, column=2, sticky="W")

        return tree

    def clear_model_explorer(self):
        tree = self.model_explorer
        tree.delete(*tree.get_children())

    def update_model_explorer(self):
        #clean an existing tree in case something is getting updated, such as
        #face reduction
        self.clear_model_explorer()
        tree = self.model_explorer
        for reference,model_placement in self.scene.model_placements.items():
            #print(model_placement.reference)
            model_root = tree.insert("", 1, model_placement.reference, text=model_placement.reference, open=True)
            model = model_placement.model

            for i,face in enumerate(model.faces):
                tree.insert(
                    model_root,
                    "end",
                    model_placement.reference + "-" + str(i),
                    text=model_placement.hash_face(i),
                    values=(face.get_unit_normal(),),
                    tags=("face",)
                )

    def keydown(self,event):
        if DEBUG:
            if event.keysym_num > 0 and event.keysym_num < 60000:
                print('This is a printable key. The character is: %r keysym: %r %r' % \
                    (event.char, event.keysym, event.keysym_num))
            else:
                print('This key is unprintable. The character is: %r keysym: %r %r' % \
                    (event.char, event.keysym, event.keysym_num))

        if event.char == '-':
            self.scene_viewer.zoom_in(1)
        if event.char == '+':
            self.scene_viewer.zoom_out(1)
        if event.char == 'w':
            self.scene_viewer.move(0,-1)
        if event.char == 'd':
            self.scene_viewer.move(-1,0)
        if event.char == 's':
            self.scene_viewer.move(0,1)
        if event.char == 'a':
            self.scene_viewer.move(1,0)
        if event.char == '\r':
            self.flatten_model()

        self.scene_viewer.update()

    def on_toggle_grid(self):
        self.scene_viewer.toggle_show_grid()
        self.scene_viewer.update()

    def on_toggle_normals(self):
        self.scene_viewer.toggle_show_normals()
        self.scene_viewer.update()

    def on_set_perspective(self, perspective):
        self.scene_viewer.set_perspective(perspective)
        self.scene_viewer.update()

    def on_toggle_model_explorer(self):
        #this doesn't work quite right, when the widget is re-packed it
        #comes back to the right of the model_viewer
        #either need to nested frames or switch to grid layout
        #not gonna bother now
        return
        if self.model_explorer.winfo_manager():
            self.model_explorer.pack_forget()
        else:
            self.model_explorer.pack()

    def on_flatten_model(self):
        """ called when flatten model is selected from menu
            allows for other processing if needed
        """
        self.flatten_model()
        self.scene_viewer.update()
        self.update_model_explorer()

    def flatten_model(self):
        for reference,model_placement in self.scene.model_placements.items():
            model = model_placement.model
            reduced_model = model.get_reduced_model()
            model_placement.model = reduced_model

    def on_export(self):
        if 0 == len(self.scene.model_placements):
            raise Exception("nothing to export")

        filename = filedialog.asksaveasfilename(filetypes=[("SVG files", "*.svg")])

        if filename:
            #gotta rework this so we know the dimensions in advance
            #chicken egg problem
            #size is apparently how we set the units, but we don't know size
            #until we've gone through the 2d coordinates.
            #will rework soon. For now, I'm hard-coding arbitrary dimensions.
            dwg = svgwrite.Drawing(filename,size=("200mm","200mm"), viewBox=("0 0 200 200"))
        else:
            return

        groups = []

        last_x, last_y = (0.0,0.0)
        margin = 2
        #todo replace w/ width (of viewBox)
        per_row = 5
        items_in_row = 0
        max_y_in_row = 0.0

        for reference,placement in self.scene.model_placements.items():
            for index,face in enumerate(placement.model.faces):
                items_in_row = items_in_row + 1
                poly_2d = face.to2D()
                poly_points = poly_2d.get_points()

                #try converting to normal floats, dwg validator does not recognize numpy.float32
                poly_points = [[float(coord) for coord in point] for point in poly_points[:-1]]
                mid_x = sum([point[0] for point in poly_points])/len(poly_points)
                mid_y = sum([point[1] for point in poly_points])/len(poly_points)
                range_x = [min([point[0] for point in poly_points]),max([point[0] for point in poly_points])]
                range_y = [min([point[1] for point in poly_points]),max([point[1] for point in poly_points])]
                label = placement.reference + '-' + placement.hash_face(index)
                group = svgwrite.container.Group(id=label,transform='translate(' + str(last_x + margin) + ',' + str(last_y + margin) + ')')
                group.add(dwg.polygon(poly_points,stroke="rgb(0,0,200)",fill="none", stroke_width=".5pt"))

                group.add(
                    dwg.text(
                        label,
                        insert=(float(mid_x),float(mid_y)),
                        font_size="6px",
                        fill="rgb(200,0,0)"
                    )
                )

                groups.append(group)

                if per_row <= items_in_row:
                    last_x = 0.0
                    items_in_row = 0
                    last_y = last_y + max_y_in_row
                    max_y_in_row = 0.0

                else:
                    last_x = last_x + (range_x[1] - range_x[0])
                    max_y_in_row = max(max_y_in_row,range_y[1] - range_y[0])

        for group in groups:
            dwg.add(group)

        dwg.save()

    def on_face_select(self, e):
        item = self.model_explorer.focus()
        model_placement = self.scene.get_model_placement(self.model_explorer.parent(item))
        model_placement.set_active_face(int(self.model_explorer.item(item,"text"),0))
        self.scene_viewer.update()

    def on_open(self):
        filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("STL files", "*.stl"),("all files","*.*")))
        my_mesh = mesh.Mesh.from_file(filename)
        model = model_from_mesh(my_mesh)

        self.scene.add_model("my_model",model,(0,0,0),None)
        self.scene_viewer.update()
        self.update_model_explorer()

    def test(self):
        print("testing")
        my_mesh = mesh.Mesh.from_file("//ORCHID/home/development/faceyanker/source-files/testcube_35mm.stl")
        model = model_from_mesh(my_mesh)
        self.scene.add_model("my_model",model,(0,0,0),None)
        self.scene_viewer.update()
        self.flatten_model()

def main():
    root = Tk()
    root.geometry("1200x800+300+10")
    app = FaceYankerApp(root,test=False)

if __name__ == '__main__':
    main()

#w = Label(root, text="Hello, world!")
#w.pack()

#root.mainloop()
