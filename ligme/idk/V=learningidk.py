import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Velocity Tester")

# ----- Inputs -----
tk.Label(root, text="Distance (meters)").pack()
distance_entry = tk.Entry(root)
distance_entry.pack()

tk.Label(root, text="Time (seconds)").pack()
time_entry = tk.Entry(root)
time_entry.pack()

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=8)
direction = tk.StringVar(value="right")
tk.Label(root, text="Acceleration (m/s²)").pack()
acc_entry = tk.Entry(root)
acc_entry.insert(0, "0")  # default = no acceleration
acc_entry.pack()


tk.Label(root, text="Direction").pack()
tk.OptionMenu(root, direction, "right", "left").pack()

canvas = tk.Canvas(root, width=300, height=80, bg="white")
canvas.pack(pady=6)

# starting dot
dot = canvas.create_oval(10, 30, 20, 40, fill="red")



# ----- Calculate Speed -----
def calculate_speed():
    try:
        d = float(distance_entry.get())
        t = float(time_entry.get())

        if t == 0:
            return messagebox.showerror("Error", "Time cannot be zero")

        speed = d / t

        result_label.config(text=f"Speed = {round(speed, 2)} m/s")
        animate_motion(speed)
        



    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers")


tk.Button(root, text="Calculate Speed", command=calculate_speed).pack(pady=6)
def animate_motion(speed):
    canvas.coords(dot, 10, 30, 20, 40)  # reset position
    x = 10
    v = speed   # starting velocity

    try:
        a = float(acc_entry.get())  # acceleration
    except:
        a = 0

    dir_value = direction.get()

    if dir_value == "left":
        v = -abs(v)
        a = -abs(a)
    else:
        v = abs(v)
        a = abs(a)

    def step():
        nonlocal x, v

        v += a        # velocity changes over time
        x += v        # position changes by velocity

        canvas.coords(dot, x, 30, x+10, 40)

        if 0 < x < 260:
            root.after(50, step)

    step()




root.mainloop()
