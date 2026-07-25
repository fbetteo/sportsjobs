"""Quick interactive analysis of users.signup_funnel_answers_json."""

# %%
import json
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Use "localhost" when connected through the repo's SSH tunnel.
DB_HOST = "localhost"
LIMIT = None  # Set to a number while exploring, for example 500.


# %% Get the data
connection = psycopg2.connect(
    host=DB_HOST,
    port=os.getenv("HETZNER_POSTGRES_PORT"),
    dbname=os.getenv("HETZNER_POSTGRES_DB"),
    user=os.getenv("HETZNER_POSTGRES_USER"),
    password=os.getenv("HETZNER_POSTGRES_PASSWORD"),
)

query = """
    SELECT signup_funnel_answers_json
    FROM users
    WHERE signup_funnel_answers_json IS NOT NULL
"""
params = None
if LIMIT is not None:
    query += " LIMIT %s"
    params = (LIMIT,)

with connection.cursor() as cursor:
    cursor.execute(query, params)
    df = pd.DataFrame(
        cursor.fetchall(),
        columns=["signup_funnel_answers_json"],
    )

connection.close()
print(f"Rows fetched: {len(df):,}")
df.head()


# %% Parse and flatten the JSON
def parse_answer(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return value


answers = df["signup_funnel_answers_json"].map(parse_answer)
valid_answers = [answer for answer in answers if isinstance(answer, dict)]
answers_df = pd.json_normalize(valid_answers, sep=".")

print(f"Valid JSON objects: {len(answers_df):,}")
answers_df.head()


# %% Field coverage
coverage = answers_df.notna().sum().to_frame("answered")
coverage["percent"] = coverage["answered"] / len(answers_df) * 100
coverage = coverage.sort_values("answered", ascending=False)
coverage


# %% Most common answers for each field
for column in answers_df.columns:
    print(f"\n{column}")
    print(answers_df[column].dropna().astype(str).value_counts().head(10))


answers_df

# sports long
sports_long = (
    answers_df[["sportsInterests"]]
    .rename(columns={"sportsInterests": "sport"})
    .explode("sport")
    .dropna(subset=["sport"])
)

sports_long["sport"] = sports_long["sport"].str.strip()

sport_counts = sports_long["sport"].value_counts()
sport_counts

respondents = answers_df["sportsInterests"].notna().sum()

sport_summary = sport_counts.to_frame("users")
sport_summary["percent_of_respondents"] = sport_summary["users"] / respondents * 100

sport_summary.reset_index()[["sport", "percent_of_respondents"]].assign(
    percent_of_respondents=lambda x: x["percent_of_respondents"].round(0)
)
# %%

pd.DataFrame(answers_df[["hardestPart"]].value_counts()).reset_index().assign(
    percent_of_respondents=lambda x: (x["count"] / respondents * 100).round(0)
)[["hardestPart", "percent_of_respondents"]]
# %%
