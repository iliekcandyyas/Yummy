import discord
from discord.ext import commands
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math
import uuid
import os

safe_math = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
safe_math.update({"sin": np.sin, "cos": np.cos, "tan": np.tan,
                  "sqrt": np.sqrt, "log": np.log, "log10": np.log10,
                  "exp": np.exp, "abs": np.abs, "pi": np.pi, "e": np.e})

GRAPHS_DIR = "graphs"
os.makedirs(GRAPHS_DIR, exist_ok=True)

COLORS = ["#7EB8F7", "#F97B6B", "#A8E6A3", "#F7D87E", "#C9A0F7", "#F7A8D4"]

def styled_fig():
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444466")
    ax.grid(True, color="#333355", linestyle="--", linewidth=0.7)
    ax.axhline(0, color="#555577", linewidth=1)
    ax.axvline(0, color="#555577", linewidth=1)
    return fig, ax

def save_and_send(fig, prefix="graph"):
    path = os.path.join(GRAPHS_DIR, f"{prefix}_{uuid.uuid4().hex}.png")
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


class GraphCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- MULTI-FUNCTION GRAPH ----------
    # Usage: ^graph sin(x), x**2, cos(x)*2
    @commands.command(name="graph")
    async def graph(self, ctx, *, expression: str):
        expressions = [e.strip() for e in expression.split(",")]
        fig, ax = styled_fig()
        x = np.linspace(-10, 10, 600)
        success = []
        for i, expr in enumerate(expressions):
            try:
                y = eval(expr, {"__builtins__": {}}, {**safe_math, "x": x})
                ax.plot(x, y, color=COLORS[i % len(COLORS)], linewidth=2, label=f"y = {expr}")
                success.append(expr)
            except Exception as e:
                await ctx.send(f"⚠️ Skipped `{expr}`: `{e}`")
        if not success:
            return
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.set_title(", ".join([f"y = {e}" for e in success]))
        ax.legend(facecolor="#2a2a3e", labelcolor="white", edgecolor="#444466")
        ax.set_ylim(-20, 20)
        path = save_and_send(fig, "graph")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- POINT ----------
    @commands.command(name="point")
    async def point(self, ctx, x_value: float, y_value: float):
        fig, ax = styled_fig()
        ax.scatter([x_value], [y_value], color=COLORS[0], s=80, zorder=5)
        ax.annotate(f"({x_value}, {y_value})", (x_value, y_value),
                    textcoords="offset points", xytext=(8, 8), color="white")
        ax.set_xlim(x_value - 5, x_value + 5)
        ax.set_ylim(y_value - 5, y_value + 5)
        ax.set_title(f"Point ({x_value}, {y_value})")
        path = save_and_send(fig, "point")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- MULTIPLE POINTS ----------
    @commands.command(name="points")
    async def points(self, ctx, *values: float):
        if len(values) % 2 != 0:
            return await ctx.send("❌ Provide pairs: `^points x y x y …`")
        xs = values[0::2]; ys = values[1::2]
        fig, ax = styled_fig()
        ax.scatter(xs, ys, color=COLORS[0], s=80, zorder=5)
        for x, y in zip(xs, ys):
            ax.annotate(f"({x}, {y})", (x, y), textcoords="offset points",
                        xytext=(8, 8), color="white", fontsize=9)
        ax.set_title("Multiple Points")
        path = save_and_send(fig, "points")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- LINE ----------
    @commands.command(name="line")
    async def line(self, ctx, x1: float, y1: float, x2: float, y2: float):
        fig, ax = styled_fig()
        ax.plot([x1, x2], [y1, y2], color=COLORS[0], linewidth=2)
        ax.scatter([x1, x2], [y1, y2], color=COLORS[1], s=80, zorder=5)
        for x, y in [(x1, y1), (x2, y2)]:
            ax.annotate(f"({x}, {y})", (x, y), textcoords="offset points",
                        xytext=(8, 8), color="white")
        ax.set_title(f"Line: ({x1},{y1}) → ({x2},{y2})")
        path = save_and_send(fig, "line")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- GRAPH + POINTS ----------
    @commands.command(name="graphpoints")
    async def graphpoints(self, ctx, expression: str, *values: float):
        if len(values) % 2 != 0:
            return await ctx.send("❌ Provide x y pairs after the function")
        xs = values[0::2]; ys = values[1::2]
        fig, ax = styled_fig()
        x = np.linspace(-10, 10, 600)
        try:
            y = eval(expression, {"__builtins__": {}}, {**safe_math, "x": x})
            ax.plot(x, y, color=COLORS[0], linewidth=2, label=f"y = {expression}")
        except Exception as e:
            return await ctx.send(f"❌ Error: `{e}`")
        ax.scatter(xs, ys, color=COLORS[1], s=80, zorder=5, label="Points")
        for a, b in zip(xs, ys):
            ax.annotate(f"({a}, {b})", (a, b), textcoords="offset points",
                        xytext=(8, 8), color="white", fontsize=9)
        ax.set_ylim(-20, 20)
        ax.legend(facecolor="#2a2a3e", labelcolor="white", edgecolor="#444466")
        ax.set_title(f"y = {expression} with points")
        path = save_and_send(fig, "gp")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- RECTANGLE ----------
    @commands.command(name="rect")
    async def rect(self, ctx, x1: float, y1: float, x2: float, y2: float):
        xs = [x1, x2, x2, x1, x1]; ys = [y1, y1, y2, y2, y1]
        width = abs(x2 - x1); height = abs(y2 - y1)
        fig, ax = styled_fig()
        ax.plot(xs, ys, color=COLORS[2], linewidth=2)
        ax.scatter(xs[:-1], ys[:-1], color=COLORS[1], s=60, zorder=5)
        for x, y in zip(xs[:-1], ys[:-1]):
            ax.annotate(f"({x},{y})", (x, y), textcoords="offset points",
                        xytext=(5, 5), color="white", fontsize=9)
        ax.text(min(xs), max(ys) + 1,
                f"Width={width}  Height={height}\nPerimeter={2*(width+height)}  Area={width*height}",
                color="white", fontsize=10,
                bbox=dict(facecolor="#2a2a3e", edgecolor="#444466", alpha=0.9))
        ax.set_title("Rectangle")
        path = save_and_send(fig, "rect")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- TRIANGLE ----------
    @commands.command(name="triangle")
    async def triangle(self, ctx, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        pts = [(x1,y1),(x2,y2),(x3,y3),(x1,y1)]
        a = math.dist(pts[0], pts[1])
        b = math.dist(pts[1], pts[2])
        c = math.dist(pts[2], pts[0])
        peri = a + b + c; s = peri / 2
        area = math.sqrt(max(s*(s-a)*(s-b)*(s-c), 0))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        fig, ax = styled_fig()
        ax.plot(xs, ys, color=COLORS[4], linewidth=2)
        ax.scatter(xs[:-1], ys[:-1], color=COLORS[1], s=60, zorder=5)
        for x, y in pts[:-1]:
            ax.annotate(f"({x},{y})", (x, y), textcoords="offset points",
                        xytext=(5, 5), color="white", fontsize=9)
        ax.text(min(xs), max(ys) + 1,
                f"Sides={round(a,2)}, {round(b,2)}, {round(c,2)}\nPerimeter={round(peri,2)}  Area={round(area,2)}",
                color="white", fontsize=10,
                bbox=dict(facecolor="#2a2a3e", edgecolor="#444466", alpha=0.9))
        ax.set_title("Triangle")
        path = save_and_send(fig, "tri")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- BAR CHART ----------
    # Usage: ^bar apples 5 bananas 3 cherries 8
    @commands.command(name="bar")
    async def bar(self, ctx, *, data: str):
        parts = data.split()
        if len(parts) % 2 != 0:
            return await ctx.send("❌ Use: `^bar label value label value …`\nExample: `^bar apples 5 bananas 3`")
        try:
            labels = parts[0::2]
            values = [float(v) for v in parts[1::2]]
        except ValueError:
            return await ctx.send("❌ Values must be numbers. Example: `^bar apples 5 bananas 3`")
        fig, ax = styled_fig()
        bars = ax.bar(labels, values, color=COLORS[:len(labels)], edgecolor="#1e1e2e", linewidth=1.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values)*0.02,
                    str(val), ha="center", color="white", fontsize=10, fontweight="bold")
        ax.set_title("Bar Chart")
        ax.set_ylabel("Value")
        ax.tick_params(axis="x", colors="white")
        path = save_and_send(fig, "bar")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    # ---------- PIE CHART ----------
    # Usage: ^pie apples 5 bananas 3 cherries 8
    @commands.command(name="pie")
    async def pie(self, ctx, *, data: str):
        parts = data.split()
        if len(parts) % 2 != 0:
            return await ctx.send("❌ Use: `^pie label value label value …`\nExample: `^pie apples 5 bananas 3`")
        try:
            labels = parts[0::2]
            values = [float(v) for v in parts[1::2]]
        except ValueError:
            return await ctx.send("❌ Values must be numbers. Example: `^pie apples 5 bananas 3`")
        fig, ax = plt.subplots(figsize=(7, 7))
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=COLORS[:len(labels)],
            autopct="%1.1f%%", startangle=140,
            wedgeprops=dict(edgecolor="#1e1e2e", linewidth=2)
        )
        for text in texts:
            text.set_color("white")
        for at in autotexts:
            at.set_color("#1e1e2e"); at.set_fontweight("bold")
        ax.set_title("Pie Chart", color="white", fontsize=14)
        path = save_and_send(fig, "pie")
        await ctx.send(file=discord.File(path))
        os.remove(path)

    #----------lineargraph------

@commands.command(name="lgraph")
async def lgraph(self, ctx, x1: float, y1: float, x2: float, y2: float):
    fig, ax = styled_fig()
    ax.plot([x1, x2], [y1, y2], color=COLORS[0], linewidth=2)
    ax.scatter([x1, x2], [y1, y2], color=COLORS[1], s=80, zorder=5)
    for x, y in [(x1, y1), (x2, y2)]:
        ax.annotate(f"({x}, {y})", (x, y), textcoords="offset points",
                    xytext=(8, 8), color="white")
    ax.set_title(f"Line: ({x1},{y1}) → ({x2},{y2})")
    path = save_and_send(fig, "lgraph")
    await ctx.send(file=discord.File(path))
    os.remove(path)


    # ---------- HELP ----------
    @commands.command(name="graphhelp")
    async def graphhelp(self, ctx):
        embed = discord.Embed(title="📊 Graph Commands", color=0x7EB8F7)
        embed.set_footer(text="Separate multiple functions with commas")
        cmds = [
            ("^graph sin(x), x**2", "Plot one or more functions"),
            ("^point 3 5", "Plot a single point"),
            ("^points 1 2 3 4 5 6", "Plot multiple points"),
            ("^line x1 y1 x2 y2", "Draw a line between two points"),
            ("^graphpoints sin(x) 0 0 1 1", "Function + overlay points"),
            ("^rect x1 y1 x2 y2", "Draw a rectangle with stats"),
            ("^triangle x1 y1 x2 y2 x3 y3", "Draw a triangle with stats"),
            ("^bar apples 5 bananas 3", "Bar chart from label/value pairs"),
            ("^pie apples 5 bananas 3", "Pie chart from label/value pairs"),
        ]
        for name, val in cmds:
            embed.add_field(name=f"`{name}`", value=val, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GraphCog(bot))
