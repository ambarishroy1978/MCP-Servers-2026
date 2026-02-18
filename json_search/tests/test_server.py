"""Basic tests for the MCP server."""

import pytest
import asyncio
from typing import List, Dict, Any

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sample.tools import get_weather, calculate_statistics, analyze_text
from src.sample.models import WeatherData, StatisticsResult, TextAnalysisResult
from framework.core.utils import (
    ValidationError,
    setup_logging,
    set_app_logger,
)
from framework.core.config import get_log_level

# Set up logging for tests (similar to src/server.py)
test_logger = setup_logging(
    log_level=get_log_level(),
    log_file=None  # Don't write to file during tests
)
set_app_logger(test_logger)


class TestWeatherTool:
    """Test cases for the weather tool."""
    
    @pytest.mark.asyncio
    async def test_get_weather_with_demo_key(self):
        result = await get_weather("London")
        
        assert isinstance(result, WeatherData)
        assert result.location == "London"
        assert result.temperature == 22.5
        assert result.description == "Partly cloudy (demo data)"
    
    @pytest.mark.asyncio
    async def test_get_weather_empty_location(self):
        """Test weather tool with empty location."""
        with pytest.raises(ValidationError, match="Location cannot be empty"):
            await get_weather("")
    
    @pytest.mark.asyncio
    async def test_get_weather_whitespace_location(self):
        """Test weather tool with whitespace location."""
        with pytest.raises(ValidationError, match="Location cannot be empty"):
            await get_weather("   ")


class TestStatisticsTool:
    """Test cases for the statistics tool."""
    
    @pytest.mark.asyncio
    async def test_calculate_statistics_basic(self):
        """Test statistics calculation with basic input."""
        numbers = [1, 2, 3, 4, 5]
        result = await calculate_statistics(numbers)
        
        assert isinstance(result, StatisticsResult)
        assert result.count == 5
        assert result.sum == 15.0
        assert result.mean == 3.0
        assert result.median == 3.0
        assert result.min == 1.0
        assert result.max == 5.0
        assert result.variance == 2.5
        assert result.std_dev == pytest.approx(1.5811, rel=1e-3)
    
    @pytest.mark.asyncio
    async def test_calculate_statistics_single_number(self):
        """Test statistics calculation with single number."""
        result = await calculate_statistics([42.0])
        
        assert result.count == 1
        assert result.sum == 42.0
        assert result.mean == 42.0
        assert result.variance == 0.0
        assert result.std_dev == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_statistics_empty_list(self):
        """Test statistics calculation with empty list."""
        with pytest.raises(ValidationError, match="Numbers list cannot be empty"):
            await calculate_statistics([])
    
    @pytest.mark.asyncio
    async def test_calculate_statistics_invalid_type(self):
        """Test statistics calculation with invalid types."""
        with pytest.raises(ValidationError, match="All elements must be numbers"):
            await calculate_statistics([1, 2, "three", 4])


class TestTextAnalysisTool:
    """Test cases for the text analysis tool."""
    
    @pytest.mark.asyncio
    async def test_analyze_text_basic(self):
        """Test text analysis with basic input."""
        text = "Hello world. This is a test."
        result = await analyze_text(text)
        
        assert isinstance(result, TextAnalysisResult)
        assert result.text == text
        assert result.word_count == 6
        assert result.char_count == 28
        assert result.char_count_no_spaces == 23
        assert result.sentence_count == 2
        assert result.average_word_length == pytest.approx(3.5, rel=1e-2)
    
    @pytest.mark.asyncio
    async def test_analyze_text_common_words(self):
        """Test text analysis for most common words."""
        text = "The quick brown fox jumps over the lazy dog. The fox is quick."
        result = await analyze_text(text, top_words=3)
        
        # Find 'the' in most common words
        the_count = next((w for w in result.most_common_words if w["word"] == "the"), None)
        assert the_count is not None
        assert the_count["count"] == 3
        
        # Check we got top 3 words
        assert len(result.most_common_words) <= 3
    
    @pytest.mark.asyncio
    async def test_analyze_text_empty(self):
        """Test text analysis with empty text."""
        with pytest.raises(ValidationError, match="Text cannot be empty"):
            await analyze_text("")
    
    @pytest.mark.asyncio
    async def test_analyze_text_whitespace(self):
        """Test text analysis with whitespace only."""
        with pytest.raises(ValidationError, match="Text cannot be empty"):
            await analyze_text("   ")


@pytest.mark.asyncio
async def test_integration():
    """Integration test running all tools."""
    # Test weather
    weather = await get_weather("Paris")
    assert weather.location == "Paris"
    
    # Test statistics
    stats = await calculate_statistics([10, 20, 30, 40, 50])
    assert stats.mean == 30.0
    
    # Test text analysis
    analysis = await analyze_text("Integration test for MCP server tools.")
    assert analysis.word_count == 6


if __name__ == "__main__":
    # Run basic integration test
    print("Running basic integration test...")
    asyncio.run(test_integration())
    print("Integration test passed!")
    
    # Run pytest if available
    try:
        import pytest
        pytest.main([__file__, "-v", "--disable-warnings"])
    except ImportError:
        print("\nInstall pytest to run full test suite: pip install pytest pytest-asyncio")
