import pandas as pd
import sqlite3
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import numpy as np


# class Analysis:
def time_range(period, unit):
    end_date = datetime.now().date()
    if unit in ["day", "days"]:
        start_date = end_date - relativedelta(days=period)

    elif unit in ["week", "weeks"]:
        start_date = end_date - relativedelta(weeks=period)

    elif unit in ["month", "months"]:
        start_date = end_date - relativedelta(months=period)

    elif unit in ["year", "years"]: 
        start_date = end_date - relativedelta(years=period)

    else:
        # need to think how to make it cleaner
        start_date = end_date - relativedelta(years=1000)

    return (start_date, end_date)


def stats():
    """
    
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('CashFlow.db')

    # Define the date range for the last week
    params = time_range(30, "day")

    # Build the SQL query to select data within the date range
    query = "SELECT * FROM transactions_data WHERE amount < 0 AND transaction_time BETWEEN ? AND ?"

    # Load the data into a Pandas DataFrame
    df = pd.read_sql_query(query, conn, params=params)

    # Close the database connection
    conn.close()

    grouped = df.groupby(by="original_mcc", as_index=False)["amount"].sum().sort_values("amount")

    print(grouped)

    # return open("df_styledw2.png", "rb")
    # grouped.show

    import dataframe_image as dfi
    dfi.export(grouped, 'tmp/groupby_cat_table.png', table_conversion="matplotlib")
    # return 
    # return grouped.to_markdown(index=False)

    # table_str = format_table(grouped)
    # print(table_str)
    # .reset_index(name="sum")
    
    # .sort_values(by=["amount"])

    # print(df) .apply(lambda x: np.sum(np.abs(x)))


    # largest = df.loc[df['amount'] == df["amount"].min()]
    # smallest = df.loc[df['amount'] == df["amount"].max()]

    # print(smallest, largest)

    # stats_msg = f"""
    # During {params[0]} {params[1]} period the smallest transaction was:
    # {smallest} UAH - 

    # """

    # stats_msg = f"""Spending distribution during {params[0]} {params[1]} period: \n
    # {grouped.to_html(index=False)}
    # """

    # print(stats_msg)






if __name__ == "__main__":
    print(stats())
