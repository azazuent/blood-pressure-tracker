from datetime import datetime

from src.database.models import Measurement
from src.services.report_generator import ReportGenerator


class TestReportGenerator:
    """Test CSV report generation functionality."""

    def test_empty_measurements(self):
        """Test report generation with no measurements."""
        generator = ReportGenerator()
        result = generator.generate_csv_report([])

        assert "Date,Time,Systolic (mmHg),Diastolic (mmHg),Reading,Category" in result

    def test_single_measurement(self):
        """Test report generation with one measurement."""
        measurement = Measurement(
            user_id=1,
            systolic=120,
            diastolic=80,
            measured_at=datetime(2023, 12, 1, 10, 30, 0)
        )

        generator = ReportGenerator()
        result = generator.generate_csv_report([measurement])

        assert "2023-12-01" in result
        assert "10:30:00" in result
        assert "120" in result
        assert "80" in result
        assert "120/80" in result
        assert "Normal" in result

    def test_multiple_measurements_sorting(self):
        """Test that measurements are sorted by date (most recent first)."""
        measurement1 = Measurement(
            user_id=1,
            systolic=120,
            diastolic=80,
            measured_at=datetime(2023, 12, 1, 10, 0, 0)
        )
        measurement2 = Measurement(
            user_id=1,
            systolic=130,
            diastolic=85,
            measured_at=datetime(2023, 12, 2, 15, 0, 0)
        )

        generator = ReportGenerator()
        result = generator.generate_csv_report([measurement1, measurement2])

        # Check that the more recent measurement appears first in CSV
        lines = result.split('\n')
        data_lines = [line for line in lines if line and not line.startswith('Date')
                     and not line.startswith('SUMMARY') and not line.startswith('Metric')]

        assert '2023-12-02' in data_lines[0]  # More recent date first

    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        measurements = [
            Measurement(user_id=1, systolic=120, diastolic=80,
                       measured_at=datetime(2023, 12, 1)),
            Measurement(user_id=1, systolic=130, diastolic=85,
                       measured_at=datetime(2023, 12, 2)),
            Measurement(user_id=1, systolic=110, diastolic=75,
                       measured_at=datetime(2023, 12, 3))
        ]

        generator = ReportGenerator()
        result = generator.generate_csv_report(measurements)

        assert "SUMMARY STATISTICS" in result
        assert "Average Systolic,120.0" in result
        assert "Average Diastolic,80.0" in result
        assert "Highest Systolic,130" in result
        assert "Lowest Systolic,110" in result

    def test_bp_category_classification(self):
        """Test blood pressure category classification in reports."""
        generator = ReportGenerator()

        assert generator._get_bp_category(110, 70) == "Normal"
        assert generator._get_bp_category(125, 75) == "Elevated"
        assert generator._get_bp_category(135, 85) == "High Blood Pressure Stage 1"
        assert generator._get_bp_category(150, 95) == "High Blood Pressure Stage 2"
        assert generator._get_bp_category(190, 125) == "Hypertensive Crisis"
