"""
Tests for location parser utility.

Tests location parsing for various formats and countries, region detection,
and normalization functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.processor.utils.location_parser import (
    parse_location,
    parse_us_location,
    parse_china_location,
    parse_generic_location,
    detect_region_from_country,
    normalize_location
)


class TestUSLocationParsing:
    """Tests for US location parsing."""
    
    def test_city_state_abbreviation(self):
        """Test parsing 'City, ST' format."""
        result = parse_us_location("Cambridge, MA")
        assert result["city"] == "Cambridge"
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_city_state_full_name(self):
        """Test parsing 'City, State' format."""
        result = parse_us_location("Boston, Massachusetts")
        assert result["city"] == "Boston"
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_state_abbreviation_only(self):
        """Test parsing state abbreviation only."""
        result = parse_us_location("MA")
        assert result["city"] is None
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_state_name_only(self):
        """Test parsing state name only."""
        result = parse_us_location("California")
        assert result["city"] is None
        assert result["state"] == "CA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_city_only(self):
        """Test parsing city only."""
        # Use a city that's not also a state name
        result = parse_us_location("Seattle")
        assert result["city"] == "Seattle"
        assert result["state"] is None
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_us_location("")
        assert result["city"] is None
        assert result["state"] is None
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_various_state_formats(self):
        """Test various state formats."""
        test_cases = [
            ("New York, NY", "New York", "NY"),
            ("Los Angeles, CA", "Los Angeles", "CA"),
            ("Chicago, Illinois", "Chicago", "IL"),
            ("Houston, Texas", "Houston", "TX"),
        ]
        
        for location_str, expected_city, expected_state in test_cases:
            result = parse_us_location(location_str)
            assert result["city"] == expected_city
            assert result["state"] == expected_state
            assert result["country"] == "United States"
            assert result["region"] == "united_states"


class TestChinaLocationParsing:
    """Tests for China location parsing."""
    
    def test_chinese_city_with_keyword(self):
        """Test parsing Chinese city with 市 keyword."""
        result = parse_china_location("北京市")
        assert result["city"] is None
        assert result["province"] == "北京市"
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_chinese_location_with_separator(self):
        """Test parsing Chinese location with separator."""
        result = parse_china_location("北京, 中国")
        assert result["city"] == "北京"
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_chinese_province_keyword(self):
        """Test parsing Chinese location with province keyword."""
        result = parse_china_location("广东省")
        assert result["city"] is None
        assert result["province"] == "广东省"
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_english_china_location(self):
        """Test parsing English China location."""
        result = parse_china_location("Beijing, China")
        assert result["city"] == "Beijing"
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_china_location("")
        assert result["city"] is None
        assert result["province"] is None
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"


class TestGenericLocationParsing:
    """Tests for generic location parsing (other countries)."""
    
    def test_uk_location(self):
        """Test parsing UK location."""
        result = parse_generic_location("London, United Kingdom", "United Kingdom")
        assert result["city"] == "London"
        assert result["country"] == "United Kingdom"
        assert result["region"] == "united_kingdom"
    
    def test_canada_location(self):
        """Test parsing Canada location."""
        result = parse_generic_location("Toronto, Canada", "Canada")
        assert result["city"] == "Toronto"
        assert result["country"] == "Canada"
        assert result["region"] == "canada"
    
    def test_australia_location(self):
        """Test parsing Australia location."""
        result = parse_generic_location("Sydney, Australia", "Australia")
        assert result["city"] == "Sydney"
        assert result["country"] == "Australia"
        assert result["region"] == "australia"
    
    def test_unknown_country(self):
        """Test parsing unknown country."""
        result = parse_generic_location("Paris, France", "France")
        assert result["city"] == "Paris"
        assert result["country"] == "France"
        assert result["region"] == "other_countries"
    
    def test_no_country_hint(self):
        """Test parsing without country hint."""
        result = parse_generic_location("Berlin, Germany")
        assert result["city"] == "Berlin"
        assert result["country"] == "Germany"
        assert result["region"] == "other_countries"


class TestRegionDetection:
    """Tests for region detection from country names."""
    
    def test_us_variations(self):
        """Test US country name variations."""
        test_cases = [
            "United States",
            "USA",
            "US",
            "U.S.A.",
            "U.S.",
        ]
        for country in test_cases:
            region = detect_region_from_country(country)
            assert region == "united_states"
    
    def test_china_variations(self):
        """Test China country name variations."""
        test_cases = [
            "China",
            "PRC",
            "People's Republic of China",
        ]
        for country in test_cases:
            region = detect_region_from_country(country)
            assert region == "mainland_china"
    
    def test_uk_variations(self):
        """Test UK country name variations."""
        test_cases = [
            "United Kingdom",
            "UK",
            "Britain",
            "Great Britain",
            "England",
        ]
        for country in test_cases:
            region = detect_region_from_country(country)
            assert region == "united_kingdom"
    
    def test_other_regions(self):
        """Test other region detection."""
        assert detect_region_from_country("Canada") == "canada"
        assert detect_region_from_country("Australia") == "australia"
        assert detect_region_from_country("France") == "other_countries"
        assert detect_region_from_country("Germany") == "other_countries"
    
    def test_empty_country(self):
        """Test empty country."""
        assert detect_region_from_country("") == "other_countries"
        assert detect_region_from_country(None) == "other_countries"


class TestMainParseLocation:
    """Tests for main parse_location function (routing logic)."""
    
    def test_us_with_country_hint(self):
        """Test parsing US location with country hint."""
        result = parse_location("Cambridge, MA", country="United States")
        assert result["city"] == "Cambridge"
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_us_without_country_hint(self):
        """Test parsing US location without country hint (auto-detect)."""
        result = parse_location("Boston, MA")
        assert result["city"] == "Boston"
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_us_with_country_in_string(self):
        """Test parsing US location with country in string."""
        result = parse_location("New York, NY, USA")
        assert result["city"] == "New York"
        assert result["state"] == "NY"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_china_with_country_hint(self):
        """Test parsing China location with country hint."""
        result = parse_location("Beijing", country="China")
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_china_with_chinese_characters(self):
        """Test parsing China location with Chinese characters."""
        result = parse_location("北京市")
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
        assert result["province"] == "北京市"
    
    def test_china_with_country_in_string(self):
        """Test parsing China location with country in string."""
        result = parse_location("Shanghai, China")
        assert result["city"] == "Shanghai"
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_uk_location(self):
        """Test parsing UK location."""
        result = parse_location("London, United Kingdom", country="United Kingdom")
        assert result["city"] == "London"
        assert result["country"] == "United Kingdom"
        assert result["region"] == "united_kingdom"
    
    def test_canada_location(self):
        """Test parsing Canada location."""
        result = parse_location("Toronto, Canada", country="Canada")
        assert result["city"] == "Toronto"
        assert result["country"] == "Canada"
        assert result["region"] == "canada"
    
    def test_other_country(self):
        """Test parsing other country."""
        result = parse_location("Paris, France", country="France")
        assert result["city"] == "Paris"
        assert result["country"] == "France"
        assert result["region"] == "other_countries"
    
    def test_empty_location(self):
        """Test parsing empty location."""
        result = parse_location("", country="United States")
        assert result["city"] is None
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_none_location(self):
        """Test parsing None location."""
        result = parse_location(None, country="United States")
        assert result["city"] is None
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_none_location_no_country(self):
        """Test parsing None location without country."""
        result = parse_location(None)
        assert result["city"] is None
        assert result["country"] == "Unknown"
        assert result["region"] == "other_countries"


class TestNormalizeLocation:
    """Tests for location normalization."""
    
    def test_string_input(self):
        """Test normalizing string input."""
        result = normalize_location("Cambridge, MA")
        assert result["city"] == "Cambridge"
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_dict_input_complete(self):
        """Test normalizing complete dictionary."""
        location_dict = {
            "city": "Boston",
            "state": "MA",
            "country": "United States",
            "region": "united_states"
        }
        result = normalize_location(location_dict)
        # normalize_location adds province key (None for US) to match schema
        expected = {
            "city": "Boston",
            "state": "MA",
            "province": None,
            "country": "United States",
            "region": "united_states"
        }
        assert result == expected
    
    def test_dict_input_missing_region(self):
        """Test normalizing dictionary with missing region (auto-detect)."""
        location_dict = {
            "city": "Boston",
            "state": "MA",
            "country": "United States"
        }
        result = normalize_location(location_dict)
        assert result["city"] == "Boston"
        assert result["state"] == "MA"
        assert result["country"] == "United States"
        assert result["region"] == "united_states"
    
    def test_dict_input_missing_country(self):
        """Test normalizing dictionary with missing country (infer from region)."""
        location_dict = {
            "city": "London",
            "region": "united_kingdom"
        }
        result = normalize_location(location_dict)
        assert result["city"] == "London"
        assert result["country"] == "United Kingdom"
        assert result["region"] == "united_kingdom"
    
    def test_china_dict(self):
        """Test normalizing China location dictionary."""
        location_dict = {
            "city": "Beijing",
            "province": "北京市",
            "country": "China"
        }
        result = normalize_location(location_dict)
        assert result["city"] == "Beijing"
        assert result["province"] == "北京市"
        assert result["country"] == "China"
        assert result["region"] == "mainland_china"
    
    def test_empty_dict(self):
        """Test normalizing empty dictionary."""
        result = normalize_location({})
        assert result["city"] is None
        assert result["country"] == "Unknown"
        assert result["region"] == "other_countries"
    
    def test_none_input(self):
        """Test normalizing None input."""
        result = normalize_location(None)
        assert result["city"] is None
        assert result["country"] == "Unknown"
        assert result["region"] == "other_countries"


def run_tests():
    """Run all tests and print results."""
    print("Testing Location Parser Utility")
    print("=" * 60)
    
    test_classes = [
        TestUSLocationParsing,
        TestChinaLocationParsing,
        TestGenericLocationParsing,
        TestRegionDetection,
        TestMainParseLocation,
        TestNormalizeLocation,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n{class_name}:")
        print("-" * 60)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            test_name = test_method.replace('test_', '').replace('_', ' ').title()
            try:
                getattr(test_instance, test_method)()
                passed_tests += 1
                print(f"  ✅ {test_name}")
            except AssertionError as e:
                failed_tests.append(f"{class_name}.{test_method}: {e}")
                print(f"  ❌ {test_name}")
                print(f"     Error: {e}")
            except Exception as e:
                failed_tests.append(f"{class_name}.{test_method}: {e}")
                print(f"  ❌ {test_name}")
                print(f"     Exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\nFailed Tests ({len(failed_tests)}):")
        for failure in failed_tests:
            print(f"  - {failure}")
        return False
    else:
        print("\n✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

