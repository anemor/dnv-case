import pandas as pd


df = pd.read_csv("/Users/mathiasotnes/Desktop/hackathon/ALL_FOUR_RESAMPLED_ais_202208/RESAMPLED_ais_202208_Bastoe I.csv", usecols=['date_time_utc', 'sog'])

df = df.sort_values(by=["date_time_utc"], ascending=True)
df["date_time_utc"] = pd.to_datetime(df["date_time_utc"], format='%Y-%m-%d %H:%M:%S')

#changing time format
for index in range(len(df)):
    df["date_time_utc"].iloc[index] = df["date_time_utc"].iloc[index].strftime('%Y-%m-%dT%H:%M:%SZ')

#swapping columns
df = df[["date_time_utc", "sog"]]
newdata = pd.DataFrame(df)
newdata.to_csv("sog.csv", index=False)