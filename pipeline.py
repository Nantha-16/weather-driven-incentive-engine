import pandas as pd
from src.weather_client import WeatherClient
from src.campaign_engine import CampaignEngine
from src.notifier import send_email

# Load control center
control_df = pd.read_csv("data/control_center.csv")

weather_client = WeatherClient()
results = []

for _, row in control_df.iterrows():
    weather_df = weather_client.fetch_weather(
        row.latitude, row.longitude
    )
    weather_df.loc[:10, "precipitation"] = 4.5
    weather_df.loc[:10, "precip_probability"] = 80


    engine = CampaignEngine(row, weather_df)
    reco = engine.evaluate()
    results.append(reco)

    if reco["comms_on"]:
        send_email(
            sender="nanthakumars2012@gmail.com",
            password="yavz pqwd papp fjdw",
            receiver=row.email,
            subject=f"Weather Alert – {row.city}",
            decision_payload=reco
            # body=f"Severe weather expected. Incentives/Comms recommended."
        )
print(weather_df.head())
final_df = pd.DataFrame(results)
final_df.to_csv("data/recommendations.csv", index=False)

print(final_df)
