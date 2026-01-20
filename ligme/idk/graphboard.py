import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
import math

safe_math = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}


# -------- HELPERS --------
def draw_axes():
    plt.axhline(0)
    plt.axvline(0)
    plt.grid(True)


# -------- GRAPH FUNCTION --------
def plot_graph():
    expr = entry_graph.get()
    x = np.linspace(-10, 10, 400)

    try:
        y = eval(expr, {"__builtins__": {}}, {**safe_math, "x": x})

        plt.figure()
        plt.plot(x, y)
        draw_axes()
        plt.title(f"y = {expr}")
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Invalid equation:\n{e}")


# -------- SINGLE POINT --------
def plot_point():
    try:
        x = float(px.get())
        y = float(py.get())

        plt.figure()
        draw_axes()
        plt.scatter([x], [y], color="red")
        plt.text(x, y, f" ({x}, {y})")
        plt.title("Point Plot")
        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers")


# -------- MULTIPLE POINTS --------
def plot_points():
    try:
        nums = list(map(float, points_input.get().split()))

        if len(nums) % 2 != 0:
            return messagebox.showerror("Error", "Enter pairs like: x y x y")

        xs = nums[0::2]
        ys = nums[1::2]

        plt.figure()
        draw_axes()
        plt.scatter(xs, ys, color="red")

        for x, y in zip(xs, ys):
            plt.text(x, y, f" ({x}, {y})")

        plt.title("Multiple Points")
        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers only")


# -------- LINE BETWEEN TWO POINTS --------
def draw_line():
    try:
        x1, y1 = float(lx1.get()), float(ly1.get())
        x2, y2 = float(lx2.get()), float(ly2.get())

        plt.figure()
        draw_axes()

        plt.scatter([x1, x2], [y1, y2], color="red")
        plt.plot([x1, x2], [y1, y2], color="blue")

        plt.text(x1, y1, f" ({x1},{y1})")
        plt.text(x2, y2, f" ({x2},{y2})")

        plt.title("Line Through Two Points")
        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers")


# -------- RECTANGLE --------
def draw_rect():
    try:
        x1, y1 = float(rx1.get()), float(ry1.get())
        x2, y2 = float(rx2.get()), float(ry2.get())

        xs = [x1, x2, x2, x1, x1]
        ys = [y1, y1, y2, y2, y1]

        width = abs(x2 - x1)
        height = abs(y2 - y1)
        area = width * height
        perimeter = 2 * (width + height)

        plt.figure()
        draw_axes()

        plt.plot(xs, ys, color="green")
        plt.scatter(xs[:-1], ys[:-1], color="red")

        for a, b in zip(xs[:-1], ys[:-1]):
            plt.text(a, b, f" ({a},{b})")

        plt.title("Rectangle")
        plt.text(min(xs), max(ys),
                 f"Width={width}\nHeight={height}\nArea={area}\nPerimeter={perimeter}")

        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers")


# -------- TRIANGLE --------
def draw_triangle():
    try:
        x1, y1 = float(tx1.get()), float(ty1.get())
        x2, y2 = float(tx2.get()), float(ty2.get())
        x3, y3 = float(tx3.get()), float(ty3.get())

        pts = [(x1,y1),(x2,y2),(x3,y3),(x1,y1)]

        a = math.dist((x1,y1),(x2,y2))
        b = math.dist((x2,y2),(x3,y3))
        c = math.dist((x3,y3),(x1,y1))

        s = (a+b+c)/2
        area = math.sqrt(max(s*(s-a)*(s-b)*(s-c), 0))
        peri = a+b+c

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]

        plt.figure()
        draw_axes()
        plt.plot(xs, ys, color="purple")
        plt.scatter(xs[:-1], ys[:-1], color="red")

        for x,y in pts[:-1]:
            plt.text(x, y, f" ({x},{y})")

        plt.title("Triangle")
        plt.text(min(xs), max(ys),
                 f"Sides={round(a,2)}, {round(b,2)}, {round(c,2)}\n"
                 f"Perimeter={round(peri,2)}\nArea={round(area,2)}")

        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers")


# -------- GRAPH + POINTS --------
def graph_plus_points():
    try:
        expr = gp_expr.get()
        nums = list(map(float, gp_points.get().split()))

        if len(nums) % 2 != 0:
            return messagebox.showerror("Error", "Enter x y pairs")

        xs = nums[0::2]; ys = nums[1::2]

        x = np.linspace(-10, 10, 400)
        y = eval(expr, {"__builtins__": {}}, {**safe_math, "x": x})

        plt.figure()
        plt.plot(x, y, color="blue")
        plt.scatter(xs, ys, color="red")

        for a,b in zip(xs, ys):
            plt.text(a, b, f" ({a},{b})")

        draw_axes()
        plt.title("Graph + Points")
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"{e}")


# -------- SIMPLE ZOOM DEMO --------
zoom = 10
def zoom_graph():
    global zoom
    zoom = max(2, zoom-2)

    x = np.linspace(-zoom, zoom, 400)
    y = x

    plt.figure()
    plt.plot(x, y)
    draw_axes()
    plt.title(f"Zoom = ±{zoom}")
    plt.show()


# -------- UI WINDOW --------
root = tk.Tk()
root.title("Math Graph Whiteboard")

# Graph
tk.Label(root, text="Equation").pack()
entry_graph = tk.Entry(root, width=30); entry_graph.pack()
tk.Button(root, text="Plot Graph", command=plot_graph).pack(pady=4)

# Single Point
tk.Label(root, text="Point x y").pack()
px = tk.Entry(root, width=8); px.pack(side="left")
py = tk.Entry(root, width=8); py.pack(side="left")
tk.Button(root, text="Plot Point", command=plot_point).pack(side="left", padx=6)

tk.Label(root, text="\nMultiple Points (x y x y)").pack()
points_input = tk.Entry(root, width=30); points_input.pack()
tk.Button(root, text="Plot Points", command=plot_points).pack()

# Line
tk.Label(root, text="\nLine x1 y1 x2 y2").pack()
lx1=tx1=tk.Entry(root,width=6); lx1.pack(side="left")
ly1=tk.Entry(root,width=6); ly1.pack(side="left")
lx2=tk.Entry(root,width=6); lx2.pack(side="left")
ly2=tk.Entry(root,width=6); ly2.pack(side="left")
tk.Button(root,text="Draw Line",command=draw_line).pack(side="left",padx=6)

# Rectangle
tk.Label(root, text="\nRectangle x1 y1 x2 y2").pack()
rx1=tk.Entry(root,width=6); rx1.pack(side="left")
ry1=tk.Entry(root,width=6); ry1.pack(side="left")
rx2=tk.Entry(root,width=6); rx2.pack(side="left")
ry2=tk.Entry(root,width=6); ry2.pack(side="left")
tk.Button(root,text="Draw Rectangle",command=draw_rect).pack(side="left",padx=6)

# Triangle
tk.Label(root, text="\nTriangle x1 y1 x2 y2 x3 y3").pack()
tx1=tk.Entry(root,width=6); tx1.pack(side="left")
ty1=tk.Entry(root,width=6); ty1.pack(side="left")
tx2=tk.Entry(root,width=6); tx2.pack(side="left")
ty2=tk.Entry(root,width=6); ty2.pack(side="left")
tx3=tk.Entry(root,width=6); tx3.pack(side="left")
ty3=tk.Entry(root,width=6); ty3.pack(side="left")
tk.Button(root,text="Draw Triangle",command=draw_triangle).pack(side="left",padx=6)

# Graph + Points
tk.Label(root, text="\nGraph + Points").pack()
gp_expr = tk.Entry(root, width=30); gp_expr.pack()
gp_points = tk.Entry(root, width=30); gp_points.pack()
tk.Button(root,text="Graph + Plot Points",command=graph_plus_points).pack()

# Zoom demo
tk.Label(root,text="\nWhiteboard Zoom Demo").pack()
tk.Button(root,text="Zoom In",command=zoom_graph).pack()

root.mainloop()


