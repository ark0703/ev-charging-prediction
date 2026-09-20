"""Demo the formula-based charging time estimator."""

from calculate_time import charging_time_minutes, format_duration


def main() -> None:
    examples = [
        {
            "label": "DC fast, airport, 28% -> 80%",
            "battery": 82,
            "soc": 28,
            "target": 80,
            "charger": "dc_fast",
            "temp": 12,
        },
        {
            "label": "Level 2, home-style, 45% -> 90%",
            "battery": 60,
            "soc": 45,
            "target": 90,
            "charger": "level2",
            "temp": 18,
        },
        {
            "label": "DC fast, cold weather, 15% -> 85%",
            "battery": 75,
            "soc": 15,
            "target": 85,
            "charger": "dc_fast",
            "temp": -2,
        },
    ]

    print("EV Charging Time Estimator")
    print("Method: time (hours) ≈ energy_kwh / average_power_kw\n")

    for item in examples:
        result = charging_time_minutes(
            item["battery"],
            item["soc"],
            item["target"],
            item["charger"],
            item["temp"],
        )
        print(item["label"])
        print(f"  Energy: {result['energy_kwh']} kWh")
        print(f"  Average power: {result['average_power_kw']} kW")
        print(f"  Estimated time: {format_duration(result['session_duration_minutes'])}")
        print()


if __name__ == "__main__":
    main()
