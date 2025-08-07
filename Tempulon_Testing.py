import unittest
from unittest.mock import patch, mock_open
from datetime import datetime

# Import your main app code
import Tempulon_Basic as tempulon

class TestTempulon(unittest.TestCase):
    # Test successful geocoding response
    @patch("Tempulon_Basic.requests.get")
    def test_get_coordinates_success(self, mock_get):
        # Simulate a valid API response with Minneapolis coordinates
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            "lat": 44.9778,
            "lon": -93.2650,
            "name": "Minneapolis"
        }]
        # Call the function and verify the output
        lat, lon, name = tempulon.get_coordinates("Minneapolis", "MN")
        self.assertEqual((lat, lon, name), (44.9778, -93.2650, "Minneapolis"))

    # Test geocoding failure (e.g., city not found)
    @patch("Tempulon_Basic.requests.get")
    def test_get_coordinates_failure(self, mock_get):
        # Simulate an empty API response
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = []
        lat, lon, name = tempulon.get_coordinates("InvalidCity")
        self.assertIsNone(lat)
        self.assertIsNone(lon)
        self.assertIsNone(name)

    # Test temperature conversion logic
    def test_convert_temperature(self):
        self.assertEqual(tempulon.convert_temperature(0, "F"), 32.0)
        self.assertEqual(tempulon.convert_temperature(100, "F"), 212.0)
        self.assertEqual(tempulon.convert_temperature(25, "C"), 25)

    # Test wind speed conversion logic
    def test_convert_wind_speed(self):
        self.assertEqual(tempulon.convert_wind_speed(1, "mph"), 2.24)
        self.assertEqual(tempulon.convert_wind_speed(0, "mph"), 0.0)
        self.assertEqual(tempulon.convert_wind_speed(5, "mps"), 5)

    # Test display_weather with no data
    def test_display_weather_none(self):
        result = tempulon.display_weather(None)
        self.assertIsNone(result)

    # Test display_weather with valid data
    def test_display_weather_valid(self):
        # Simulated weather data
        sample_data = {
            "main": {"temp": 20, "humidity": 50},
            "wind": {"speed": 5},
            "weather": [{"description": "clear sky"}]
        }
        # Check that the output string includes expected values
        result = tempulon.display_weather(sample_data, "F")
        self.assertIn("Clear sky", result)
        self.assertIn("°F", result)

    # Test saving last search to file
    @patch("builtins.open", new_callable=mock_open)
    def test_save_last_search(self, mock_file):
        tempulon.save_last_search("Minneapolis", "MN", "20°C, Clear, 50%, 11.18 mph")
        # Verify that the correct string was written
        mock_file().write.assert_called_with("Minneapolis,MN\n20°C, Clear, 50%, 11.18 mph")

    # Test loading last search from file
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="Minneapolis,MN\n20°C, Clear, 50%, 11.18 mph")
    def test_load_last_search(self, mock_file, mock_exists):
        # Capture printed output
        with patch("builtins.print") as mock_print:
            tempulon.load_last_search()
            mock_print.assert_any_call("\n Last Search: Minneapolis,MN")
            mock_print.assert_any_call("Weather: 20°C, Clear, 50%, 11.18 mph\n")

# Run the test suite
if __name__ == "__main__":
    unittest.main()