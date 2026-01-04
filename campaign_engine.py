# class CampaignEngine:
#     def __init__(self, city_config, weather_df):
#         self.cfg = city_config
#         self.df = weather_df

#     def evaluate(self):
#         avg_precip = self.df["precipitation"].mean()
#         bad_hours = (self.df["precipitation"] >= self.cfg["min_precip_mm"]).sum()
#         bad_weather_pct = bad_hours / len(self.df)

#         comms_on = (
#             avg_precip >= self.cfg["min_precip_mm"]
#             and bad_weather_pct >= self.cfg["block_threshold"]
#             and self.cfg["enabled"]
#         )

#         return {
#             "city": self.cfg["city"],
#             "avg_precip": round(avg_precip, 2),
#             "bad_weather_pct": round(bad_weather_pct * 100, 2),
#             "opt_type": self.cfg["opt_type"],
#             "cohort_size": 0.5 if comms_on else 0.0,
#             "comms_on": comms_on
#         }

class CampaignEngine:
    def __init__(self, city_config, weather_df):
        self.cfg = city_config
        self.df = weather_df

    def evaluate(self):
        avg_precip = self.df["precipitation"].mean()
        bad_hours = (self.df["precipitation"] >= self.cfg.get("min_precip_mm", 0)).sum()
        bad_weather_pct = bad_hours / len(self.df)

        # -------- SAFE CONFIG READS --------
        enabled = self.cfg.get("enabled", True)
        min_precip = self.cfg.get("min_precip_mm", 0)
        block_threshold = self.cfg.get("block_threshold", 0.3)
        max_precip = self.cfg.get("max_precip_mm", float("inf"))
        opt_type = self.cfg.get("opt_type", "opt-in")
        default_cohort = self.cfg.get("default_cohort", 0.0)

        # -------- SAFETY SUPPRESSION --------
        if avg_precip >= max_precip:
            return {
                "city": self.cfg.get("city"),
                "avg_precip": round(avg_precip, 2),
                "bad_weather_pct": round(bad_weather_pct * 100, 2),
                "opt_type": opt_type,
                "cohort_size": 0.0,
                "comms_on": True,
                "decision": "Safety Comms Only"
            }

        # -------- WEATHER QUALIFICATION --------
        weather_qualifies = (
            avg_precip >= min_precip
            or bad_weather_pct >= block_threshold
        )

        comms_on = weather_qualifies and enabled

        # -------- COHORT LOGIC --------
        cohort_size = (
            default_cohort
            if comms_on and opt_type == "opt-in"
            else 0.0
        )

        decision = (
            "Incentives + Comms"
            if cohort_size > 0
            else "Comms Only"
            if comms_on
            else "No Action"
        )

        return {
            "city": self.cfg.get("city"),
            "avg_precip": round(avg_precip, 2),
            "bad_weather_pct": round(bad_weather_pct * 100, 2),
            "opt_type": opt_type,
            "cohort_size": cohort_size,
            "comms_on": comms_on,
            "decision": decision
        }

