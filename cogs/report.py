import discord
from discord import app_commands
from discord.ext import commands
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import random
from groq import Groq
import os


def generate_fake_sales(days=14, starting_revenue=2000):
    dates = []
    revenues = []
    revenue = starting_revenue
    today = datetime.today()

    for i in range(days):
        current_date = today - timedelta(days=(days - i))
        change = random.uniform(-0.10, 0.10)
        revenue = revenue * (1 + change)
        dates.append(current_date)
        revenues.append(revenue)

    return dates, revenues


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if the bot is alive")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🏓")

    @app_commands.command(name="bitcoin_price", description="Get the lastest USD bitcoin prices")
    async def price(self, interaction: discord.Interaction):
        request = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        if request.status_code == 200:
            response = request.json()
            bitcoin_price = response["bitcoin"]["usd"]
            await interaction.response.send_message(f"The usd price of bitcoin is currenly {bitcoin_price}")
        else:
            await interaction.response.send_message("Unknown Error...")

    @app_commands.command(name="bitcoin_chart", description="Get a 7-day Bitcoin price chart")
    async def bitcoin_chart(self, interaction: discord.Interaction):
        await interaction.response.defer()

        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": 7, "interval": "daily"}
        request = requests.get(url, params=params)

        if request.status_code != 200:
            await interaction.followup.send("Couldn't fetch Bitcoin data right now.")
            return

        data = request.json()
        prices = data["prices"]

        dates = [datetime.fromtimestamp(p[0] / 1000) for p in prices]
        values = [p[1] for p in prices]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(dates, values, marker="o", linewidth=2)
        ax.set_title("Bitcoin Price (7 days)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate(rotation=30)
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close(fig)

        chart_file = discord.File(buffer, filename="bitcoin_chart.png")
        await interaction.followup.send("Here's the 7-day Bitcoin chart:", file=chart_file)

    @app_commands.command(name="bitcoin_report", description="Get a Bitcoin chart with an AI summary")
    async def bitcoin_report(self, interaction: discord.Interaction):
        await interaction.response.defer()

        
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": 7, "interval": "daily"}
        request = requests.get(url, params=params)

        if request.status_code != 200:
            await interaction.followup.send("Couldn't fetch Bitcoin data right now.")
            return

        data = request.json()
        prices = data["prices"]
        dates = [datetime.fromtimestamp(p[0] / 1000) for p in prices]
        values = [p[1] for p in prices]

        
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(dates, values, marker="o", linewidth=2)
        ax.set_title("Bitcoin Price (7 days)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate(rotation=30)
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close(fig)
        chart_file = discord.File(buffer, filename="bitcoin_chart.png")

      
        client = Groq(api_key=os.environ["GROQ_API_TOKEN"])
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=400,
            reasoning_effort="low",
            messages=[
                {
                    "role": "user",
                    "content": f"Here is 7 days of Bitcoin price data in USD: {values}. "
                                "Write a 2-3 sentence summary as if you are a business "
                                "owner reflecting on this trend. Focus on percentage "
                                "change, and keep the tone personal and direct."
                }
            ]
        )

        ai_summary_text = response.choices[0].message.content
        if not ai_summary_text:
            ai_summary_text = "Chart generated — AI summary came back empty, try again."

        
        await interaction.followup.send(content=ai_summary_text, file=chart_file)

async def setup(bot):
    await bot.add_cog(Report(bot))