import discord
from discord.ext import commands
import numpy as np
import matplotlib.pyplot as plt
import math
import uuid
import os

# allow safe math functions only
safe_math = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}

GRAPHS_DIR = "graphs"
os.makedirs(GRAPHS_DIR, exist_ok=True)

def draw_quadrants():
    plt.axhline(0, color="black")
    plt.axvline(0, color="black")
    plt.text(5, 5, "Quadrant I")
    plt.text(-9, 5, "Quadrant II")
    plt.text(-9, -5, "Quadrant III")
    plt.text(5, -5, "Quadrant IV")


class GraphCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # ---------- BASIC GRAPH ----------
    @commands.command(name="graph")
    async def graph(self, ctx, *, expression: str):
        await ctx.send(f"using brain.. plotting: `y = {expression}` …")
        try:
            x = np.linspace(-10, 10, 400)
            y = eval(expression, {"__builtins__": {}}, {**safe_math, "x": x})

            plt.figure()
            plt.plot(x, y)
            plt.title(f"y = {expression}")
            plt.xlabel("x"); plt.ylabel("y")
            plt.grid(True)

            file_path = os.path.join(GRAPHS_DIR, f"graph_{uuid.uuid4().hex}.png")
            plt.savefig(file_path); plt.close()
            await ctx.send(file=discord.File(file_path))
            os.remove(file_path)
        except Exception as e:
            await ctx.send(f"❌ Error while plotting: `{e}`")


    # ---------- POINT ----------
    @commands.command(name="point")
    async def point(self, ctx, x_value: float, y_value: float):
        await ctx.send(f"📌 pinning: ({x_value}, {y_value})")
        plt.figure()
        plt.axhline(0); plt.axvline(0)

        plt.scatter([x_value], [y_value], color="red")
        plt.text(x_value, y_value, f" ({x_value}, {y_value})")

        plt.xlim(x_value-5, x_value+5)
        plt.ylim(y_value-5, y_value+5)
        plt.grid(True); plt.xlabel("x"); plt.ylabel("y")

        file_path = os.path.join(GRAPHS_DIR, f"point_{uuid.uuid4().hex}.png")
        plt.savefig(file_path); plt.close()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)


    # ---------- MULTIPLE POINTS ----------
    @commands.command(name="points")
    async def points(self, ctx, *values: float):
        if len(values) % 2 != 0:
            return await ctx.send("❌ Please provide pairs like: x y x y …")

        xs = values[0::2]; ys = values[1::2]
        await ctx.send(f"plotting points: {list(zip(xs, ys))}")

        plt.figure()
        plt.axhline(0); plt.axvline(0)
        plt.scatter(xs, ys, color="red")

        for x, y in zip(xs, ys):
            plt.text(x, y, f" ({x}, {y})")

        plt.grid(True); plt.title("Multiple Points")
        file_path = os.path.join(GRAPHS_DIR, f"points_{uuid.uuid4().hex}.png")
        plt.savefig(file_path); plt.close()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)


    # ---------- LINE ----------
    @commands.command(name="line")
    async def line(self, ctx, x1: float, y1: float, x2: float, y2: float):
        await ctx.send(f"line through ({x1},{y1}) → ({x2},{y2})")

        xs = [x1,x2]; ys = [y1,y2]
        plt.figure()
        plt.axhline(0); plt.axvline(0)

        plt.scatter(xs, ys, color="red")
        plt.plot(xs, ys, color="blue")

        for x,y in zip(xs,ys):
            plt.text(x, y, f" ({x}, {y})")

        plt.grid(True)
        file_path = os.path.join(GRAPHS_DIR, f"line_{uuid.uuid4().hex}.png")
        plt.savefig(file_path); plt.close()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)


    # ---------- GRAPH + POINTS ----------
    @commands.command(name="graphpoints")
    async def graphpoints(self, ctx, expression: str, *values: float):
        if len(values) % 2 != 0:
            return await ctx.send("❌ Provide x y pairs after function")

        xs = values[0::2]; ys = values[1::2]
        x = np.linspace(-10,10,400)
        y = eval(expression, {"__builtins__": {}}, {**safe_math,"x":x})

        plt.figure()
        plt.plot(x,y,color="blue")
        plt.scatter(xs,ys,color="red")

        for a,b in zip(xs,ys):
            plt.text(a,b,f" ({a}, {b})")

        plt.axhline(0); plt.axvline(0); plt.grid(True)

        file_path = os.path.join(GRAPHS_DIR, f"gp_{uuid.uuid4().hex}.png")
        plt.savefig(file_path); plt.close()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)


    # ---------- RECTANGLE ----------
    @commands.command(name="rect")
    async def rect(self, ctx, x1:float,y1:float,x2:float,y2:float):
        xs=[x1,x2,x2,x1,x1]; ys=[y1,y1,y2,y2,y1]
        width=abs(x2-x1); height=abs(y2-y1)
        peri=2*(width+height); area=width*height

        plt.figure(); draw_quadrants()
        plt.plot(xs,ys,color="green"); plt.scatter(xs,ys,color="red")

        for x,y in zip(xs[:-1],ys[:-1]):
            plt.text(x,y,f" ({x},{y})")

        plt.text(min(xs),max(ys)+1,
                 f"Width={width}\nHeight={height}\nPerimeter={peri}\nArea={area}",
                 bbox=dict(facecolor='white',alpha=.7))

        file_path=os.path.join(GRAPHS_DIR,f"rect_{uuid.uuid4().hex}.png")
        plt.savefig(file_path); plt.close()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)


    # ---------- TRIANGLE ----------
    @commands.command(name="triangle")
    async def triangle(self, ctx,x1:float,y1:float,x2:float,y2:float,x3:float,y3:float):
        pts=[(x1,y1),(x2,y2),(x3,y3),(x1,y1)]
        dist=lambda a,b: math.dist(a,b)

        a=dist(pts[0],pts[1])
        b=dist(pts[1],pts[2])
        c=dist(pts[2],pts[0])

        peri=a+b+c
        s=peri/2
        area=math.sqrt(max(s*(s-a)*(s-b)*(s-c),0))

        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]

        plt.figure(); draw_quadrants()
        plt.plot(xs,ys,color="purple"); plt.scatter(xs[:-1],ys[:-1],color="red")

        for x,y in pts[:-1]:
            plt.text(x,y,f" ({x},{y})")

        plt.text(min(xs),max(ys)+1,
                 f"Sides={round(a,2)}, {round(b,2)}, {round(c,2)}\n"
                 f"Perimeter={round(peri,2)}\nArea={round(area,2)}",
                 bbox=dict(facecolor='white',alpha=.7))

        file_path=os.path.join(GRAPHS_DIR,f"tri_{uuid.uuid4().hex}.png")
        plt.savefig(file_path); plt.close()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)


    # ---------- WHITEBOARD COMMAND ----------
    @commands.command(name="whiteboard")
    async def whiteboard(self, ctx):
        await ctx.send("🧮 Math board loaded — use buttons to move & zoom")
        view = WhiteboardView()
        file = view.draw_graph()
        await ctx.send(file=discord.File(file), view=view)
        os.remove(file)


async def setup(bot):
    await bot.add_cog(GraphCog(bot))



# ---------- WHITEBOARD VIEW ----------
class WhiteboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.xmin = -10; self.xmax = 10
        self.ymin = -10; self.ymax = 10

        self.points = []   # store plotted points

    def draw_graph(self):
        x = np.linspace(self.xmin, self.xmax, 400)
        y = x

        plt.figure()
        plt.plot(x, y)

        # axes + grid
        plt.axhline(0)
        plt.axvline(0)
        plt.grid(True)

        # draw any saved points
        if self.points:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]

            plt.scatter(xs, ys, color="red")

            for x, y in self.points:
                plt.text(x, y, f" ({x}, {y})")

        # save image
        file = os.path.join("graphs", f"board_{uuid.uuid4().hex}.png")
        plt.savefig(file)
        plt.close()

        return file



    # ----- BUTTONS -----
    @discord.ui.button(label="⬅ Left")
    async def left(self, interaction, button):
        self.xmin -= 2; self.xmax -= 2
        file = self.draw_graph()
        await interaction.response.edit_message(
            attachments=[discord.File(file)],
            view=self
        )
        os.remove(file)

    @discord.ui.button(label="➡ Right")
    async def right(self, interaction, button):
        self.xmin += 2; self.xmax += 2
        file = self.draw_graph()
        await interaction.response.edit_message(
            attachments=[discord.File(file)],
            view=self
        )
        os.remove(file)

    @discord.ui.button(label="⬆ Up")
    async def up(self, interaction, button):
        self.ymin += 2; self.ymax += 2
        file = self.draw_graph()
        await interaction.response.edit_message(
            attachments=[discord.File(file)],
            view=self
        )
        os.remove(file)

    @discord.ui.button(label="⬇ Down")
    async def down(self, interaction, button):
        self.ymin -= 2; self.ymax -= 2
        file = self.draw_graph()
        await interaction.response.edit_message(
            attachments=[discord.File(file)],
            view=self
        )
        os.remove(file)

    @discord.ui.button(label="🔍 Zoom In")
    async def zoom_in(self, interaction, button):
        self.xmin += 2; self.xmax -= 2
        self.ymin += 2; self.ymax -= 2
        file = self.draw_graph()
        await interaction.response.edit_message(
            attachments=[discord.File(file)],
            view=self
        )
        os.remove(file)

    @discord.ui.button(label="🗺 Zoom Out")
    async def zoom_out(self, interaction, button):
        self.xmin -= 2; self.xmax += 2
        self.ymin -= 2; self.ymax += 2
        file = self.draw_graph()
        await interaction.response.edit_message(
            attachments=[discord.File(file)],
            view=self
        )
        os.remove(file)

    @discord.ui.button(label="📍 Place Point")
    async def place_point(self, interaction, button):

        await interaction.response.send_message(
            "Send coordinates like: `x y` (example: `3 5`)",
            ephemeral=True
        )

        def check(msg):
            return (
                msg.author.id == interaction.user.id
                and msg.channel == interaction.channel
            )

        msg = await interaction.client.wait_for("message", check=check)

        try:
            x, y = map(float, msg.content.split())
            self.points.append((x, y))
        except:
            return await interaction.followup.send(
                "❌ Invalid format — use: `x y`",
                ephemeral=True
            )

        file = self.draw_graph()

        await interaction.message.edit(
            attachments=[discord.File(file)],
            view=self
        )

        os.remove(file)


