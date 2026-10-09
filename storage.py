
import pandas as pd

CSV_FILE = "food_log.csv"

COLUMNS = [
    "Date", "Food", "Quantity", "Unit",
    "Calories", "Proteins", "Carbs", "Fat", "Fibre"
]


def load_food_log():
    try:
        df = pd.read_csv(CSV_FILE)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUMNS)


def save_food_log(df):
    df.to_csv(CSV_FILE, index=False)
