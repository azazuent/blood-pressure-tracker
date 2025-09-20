from datetime import date

from src.bot.handlers import get_bp_category, parse_blood_pressure


class TestBloodPressureParsing:
    """Test blood pressure parsing functionality."""

    def test_valid_formats(self):
        """Test parsing of valid blood pressure formats."""
        assert parse_blood_pressure("120/80") == (120, 80)
        assert parse_blood_pressure("120 / 80") == (120, 80)
        assert parse_blood_pressure("120-80") == (120, 80)
        assert parse_blood_pressure("My reading is 130/85 today") == (130, 85)

    def test_invalid_formats(self):
        """Test parsing of invalid formats."""
        assert parse_blood_pressure("hello") is None
        assert parse_blood_pressure("120") is None
        assert parse_blood_pressure("120/") is None
        assert parse_blood_pressure("/80") is None
        assert parse_blood_pressure("abc/def") is None

    def test_invalid_ranges(self):
        """Test rejection of invalid blood pressure ranges."""
        assert parse_blood_pressure("50/30") is None  # Too low
        assert parse_blood_pressure("300/200") is None  # Too high
        assert parse_blood_pressure("80/120") is None  # Inverted values

    def test_edge_cases(self):
        """Test edge cases for blood pressure values."""
        assert parse_blood_pressure("60/30") == (60, 30)  # Minimum valid
        assert parse_blood_pressure("250/150") == (250, 150)  # Maximum valid


class TestBloodPressureCategories:
    """Test blood pressure category classification."""

    def test_normal(self):
        """Test normal blood pressure category."""
        assert get_bp_category(110, 70) == "Нормальное"
        assert get_bp_category(119, 79) == "Нормальное"

    def test_elevated(self):
        """Test elevated blood pressure category."""
        assert get_bp_category(125, 75) == "Повышенное"
        assert get_bp_category(129, 79) == "Повышенное"

    def test_stage_1(self):
        """Test stage 1 hypertension."""
        assert get_bp_category(135, 85) == "Высокое АД 1-й степени"
        assert get_bp_category(139, 89) == "Высокое АД 1-й степени"

    def test_stage_2(self):
        """Test stage 2 hypertension."""
        assert get_bp_category(150, 95) == "Высокое АД 2-й степени"
        assert get_bp_category(179, 119) == "Высокое АД 2-й степени"

    def test_hypertensive_crisis(self):
        """Test hypertensive crisis category."""
        assert get_bp_category(190, 125) == "Гипертонический криз - обратитесь к врачу"
        assert get_bp_category(200, 130) == "Гипертонический криз - обратитесь к врачу"


class TestDailyMeasurementCount:
    """Test daily measurement counting functionality."""

    def test_daily_count_basic(self):
        """Test that the daily measurement count method is accessible."""
        from unittest.mock import MagicMock

        from src.database.repositories import MeasurementRepository

        # Create a mock session
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 2

        # Test the repository method
        repo = MeasurementRepository(mock_session)
        count = repo.get_daily_measurement_count(1, date.today())

        # Verify it returns a count
        assert isinstance(count, int)
        assert count == 2
