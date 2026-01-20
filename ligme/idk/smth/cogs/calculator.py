from discord.ext import commands
import discord
from sympy import sympify, symbols, Eq, solve, pi, sin, cos, tan, sqrt
from sympy.core.sympify import SympifyError


SAFE_SYMBOLS = {
    "pi": pi,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "sqrt": sqrt,
}

BUTTON_ROWS = [
    ["(", ")", "⌫", "C"],       # 4 buttons
    ["7", "8", "9", "÷"],        # 4 buttons
    ["4", "5", "6", "×"],        # 4 buttons
    ["1", "2", "3", "-"],        # 4 buttons
    ["0", ".", "^", "+"],        # 4 buttons
    ["sin", "cos", "tan"],       # 3 buttons (previously 4)
    ["√", "π", "="]              # 3 buttons (previously 2)
]

# ---------- BUTTON UI CALCULATOR ----------

class CalcView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=90)
        self.user = user
        self.expression = ""

        # Dynamically add buttons based on rows
        for row_i, row in enumerate(BUTTON_ROWS):
            if row_i >= 5:
                break  # Stop if we exceed the max rows (5)

            # Ensure each row has no more than 5 buttons
            row = row[:5]  # Limit each row to a maximum of 5 buttons

            # Add each button to the row
            for label in row:
                # Ensure that the row index doesn't exceed the limit
                self.add_item(CalcButton(label, row_i))  # Use row_i directly without wrapping



    async def update_display(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✨ Fancy Discord Calculator",
            description=f"```{self.expression or '0'}```",
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def evaluate(self, interaction: discord.Interaction):
        try:
            expr = (
                self.expression
                    .replace("^", "**")
                    .replace("×", "*")
                    .replace("÷", "/")
                    .replace("√", "sqrt")
                    .replace("π", "pi")
            )

            result = sympify(expr, locals=SAFE_SYMBOLS).evalf()
            self.expression = str(result)

        except SympifyError:
            self.expression = "Error"

        await self.update_display(interaction)


    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ This calculator belongs to someone else.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.stop()


class CalcButton(discord.ui.Button):
    def __init__(self, label: str, row: int):
        super().__init__(
            label=label,
            row=row,  # The correct row will now be passed here
            style=(
                discord.ButtonStyle.danger if label == "C"
                else discord.ButtonStyle.success if label == "="
                else discord.ButtonStyle.primary if label in ["+", "-", "×", "÷"]
                else discord.ButtonStyle.secondary
            )
        )

    async def callback(self, interaction: discord.Interaction):
        view: CalcView = self.view

        match self.label:
            case "C":
                view.expression = ""
            case "⌫":
                view.expression = view.expression[:-1]
            case "=":
                return await view.evaluate(interaction)
            case _:
                view.expression += self.label

        await view.update_display(interaction)
  # Update the display after any change



# ---------- COG WITH BOTH COMMANDS ----------

class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Text / algebra calculator
    @commands.command(aliases=["calc", "solve"])
    async def calculate(self, ctx, *, expression: str):
        x = symbols("x")

        try:
            if "=" in expression:
                left, right = expression.split("=", 1)
                eq = Eq(sympify(left), sympify(right))
                solutions = solve(eq)

                if not solutions:
                    return await ctx.send("❌ No solution found.")
                return await ctx.send(f"Solution for **x**: `{solutions}`")

            expr = sympify(expression)
            result = expr.evalf() if expr.free_symbols == set() else expr
            await ctx.send(f"= **{expression}** = `{result}`")

        except SympifyError:
            await ctx.send("❌ gng I aint Albert Einstein, use a VALID expression...")
        except Exception:
            await ctx.send("uhhh... error.. error.. *explodes*")

    # Button UI calculator
    @commands.command(name="buttoncalc", aliases=["uicalc", "calcui"])
    async def button_calc(self, ctx):
        """Open the fancy calculator UI"""
        view = CalcView(ctx.author)

        embed = discord.Embed(
            title="✨ Fancy Discord Calculator",
            description="```0```",
            color=discord.Color.blurple()
        )

        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

async def setup(bot):
    await bot.add_cog(Calculator(bot))
