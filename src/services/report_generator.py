import io
from datetime import datetime

import pandas as pd

from ..database.models import Measurement


class ReportGenerator:
    """Service for generating CSV reports from blood pressure measurements."""

    def generate_csv_report(self, measurements: list[Measurement]) -> str:
        """Generate CSV report from measurements."""
        if not measurements:
            return self._empty_csv()

        # Convert measurements to DataFrame
        data = []
        for measurement in measurements:
            data.append(
                {
                    "Date": measurement.measured_at.strftime("%Y-%m-%d"),
                    "Time": measurement.measured_at.strftime("%H:%M:%S"),
                    "Systolic (mmHg)": measurement.systolic,
                    "Diastolic (mmHg)": measurement.diastolic,
                    "Reading": measurement.formatted_reading,
                    "Category": self._get_bp_category(measurement.systolic, measurement.diastolic),
                    "Timestamp": measurement.measured_at.isoformat(),
                }
            )

        df = pd.DataFrame(data)

        # Sort by date/time (most recent first)
        df = df.sort_values("Timestamp", ascending=False)

        # Drop the timestamp column from final output
        df = df.drop("Timestamp", axis=1)

        # Add summary statistics
        summary_data = self._calculate_summary(measurements)

        # Convert to CSV string
        csv_buffer = io.StringIO()

        # Write measurements
        df.to_csv(csv_buffer, index=False)

        # Add summary section
        csv_buffer.write("\n\nSUMMARY STATISTICS\n")
        csv_buffer.write("Metric,Value\n")

        for key, value in summary_data.items():
            csv_buffer.write(f"{key},{value}\n")

        # Add generation info
        csv_buffer.write(f'\nReport generated on,{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        csv_buffer.write(f"Total measurements,{len(measurements)}\n")

        return csv_buffer.getvalue()

    def _empty_csv(self) -> str:
        """Return empty CSV with headers."""
        headers = ["Date", "Time", "Systolic (mmHg)", "Diastolic (mmHg)", "Reading", "Category"]
        return ",".join(headers) + "\n"

    def _calculate_summary(self, measurements: list[Measurement]) -> dict:
        """Calculate summary statistics for measurements."""
        if not measurements:
            return {}

        systolic_values = [m.systolic for m in measurements]
        diastolic_values = [m.diastolic for m in measurements]

        return {
            "Average Systolic": f"{sum(systolic_values) / len(systolic_values):.1f}",
            "Average Diastolic": f"{sum(diastolic_values) / len(diastolic_values):.1f}",
            "Highest Systolic": max(systolic_values),
            "Highest Diastolic": max(diastolic_values),
            "Lowest Systolic": min(systolic_values),
            "Lowest Diastolic": min(diastolic_values),
            "Most Recent Reading": f"{measurements[0].systolic}/{measurements[0].diastolic}",
            "Most Recent Date": measurements[0].measured_at.strftime("%Y-%m-%d %H:%M"),
            "Date Range (Days)": self._calculate_date_range_days(measurements),
        }

    def _calculate_date_range_days(self, measurements: list[Measurement]) -> int:
        """Calculate the range of dates in days."""
        if len(measurements) < 2:
            return 0

        sorted_measurements = sorted(measurements, key=lambda m: m.measured_at)
        first_date = sorted_measurements[0].measured_at.date()
        last_date = sorted_measurements[-1].measured_at.date()

        return (last_date - first_date).days

    def _get_bp_category(self, systolic: int, diastolic: int) -> str:
        """Get blood pressure category based on AHA guidelines."""
        if systolic <= 120 and diastolic <= 80:
            return "Normal"
        elif systolic <= 130 and diastolic <= 80:
            return "Elevated"
        elif systolic <= 140 or diastolic <= 90:
            return "High Blood Pressure Stage 1"
        elif systolic <= 180 or diastolic <= 120:
            return "High Blood Pressure Stage 2"
        else:
            return "Hypertensive Crisis"
