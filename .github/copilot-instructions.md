# Copilot Instructions for HueToInflux

## Project Overview
HueToInflux is a Python application that bridges Philips Hue smart home data to InfluxDB for time-series monitoring and visualization. It collects sensor data (temperature, light levels, presence) and light states from Hue bridges and sends them to InfluxDB using the line protocol format.

## Key Components

### Main Application (`huetoinflux.py`)
- **Bridge Connection**: Uses `phue` library to connect to Philips Hue bridges
- **Data Collection**: Gathers sensor and light data from Hue API
- **Data Processing**: Converts Hue data to InfluxDB line protocol format
- **Data Transmission**: Sends processed data to InfluxDB via HTTP POST
- **Signal Handling**: Graceful shutdown on SIGINT/SIGTERM
- **CLI Modes**: `--dump` (one-time data export) and `--print` (continuous monitoring)

### Configuration (`settings.json`)
- Hue bridge connection details (host, username)
- InfluxDB connection details (URL, database, credentials, timeout)
- Sensor name mappings for custom naming
- Temperature unit preferences (C/F/K)
- Collection interval settings

### Development Tools
- **Code Formatting**: Black with 120 character line length
- **Linting**: Flake8 with bugbear and black plugins
- **Testing**: pytest with mock support
- **Type Checking**: mypy (configured in pyproject.toml)
- **Tox**: Multi-environment testing

## Code Style & Standards

### Python Style
- Follow PEP 8 guidelines with 120 character line length (Black formatter)
- Use type hints where appropriate
- Include comprehensive docstrings for all functions with parameter and return type documentation
- Use meaningful variable and function names
- Maximum complexity of 10 (flake8 configuration)

### Error Handling
- Graceful error handling with appropriate exit codes:
  - `0`: Normal exit
  - `1`: Configuration errors (missing/invalid settings.json)
  - `2`: Connection errors (Hue bridge, InfluxDB)
- Log errors to stderr with descriptive messages
- Handle network timeouts and connection failures
- Validate configuration before processing

### Testing Requirements
- All functions must have unit tests using pytest
- Use pytest fixtures for common setup
- Mock external dependencies (Hue API, InfluxDB, HTTP requests)
- Test both success and error scenarios
- Aim for high test coverage

## Development Guidelines

### When Adding New Features
1. **Data Collection**: Add new sensor types or data fields in `parse_data()`
2. **Configuration**: Extend settings structure and validation
3. **Error Handling**: Add appropriate error cases and exit codes
4. **Testing**: Create comprehensive unit tests for new functionality
5. **Documentation**: Update docstrings and comments

### When Modifying Existing Code
1. **Backward Compatibility**: Ensure existing functionality remains intact
2. **Configuration**: Maintain backward compatibility with existing config files
3. **Error Handling**: Preserve existing error handling patterns
4. **Testing**: Update or add tests for modified functionality

### Code Organization
- Keep functions focused and single-purpose
- Use descriptive function and variable names
- Group related functionality together
- Separate concerns (data collection, processing, transmission)

## Common Patterns

### Data Processing
```python
def process_sensor_data(sensor_data):
    """
    Process raw sensor data into InfluxDB line protocol format.
    
    :param sensor_data: Raw sensor data from Hue API
    :type sensor_data: dict
    :return: Formatted data for InfluxDB
    :rtype: dict
    """
    # Extract relevant fields
    # Apply unit conversions
    # Format for InfluxDB
    return formatted_data
```

### Error Handling
```python
try:
    # Operation that might fail
    result = risky_operation()
except (SpecificException, AnotherException) as e:
    print(f"Error message: {e}")
    sys.exit(2)  # Appropriate exit code
```

### Testing Patterns
```python
def test_function_with_external_dependency(monkeypatch):
    """Test function that uses external dependency."""
    def mock_external_call():
        return expected_data
    
    monkeypatch.setattr(module, "external_function", mock_external_call)
    result = function_under_test()
    assert result == expected_result
```

## Dependencies

### Core Dependencies
- `phue~=1.1`: Philips Hue bridge communication
- `requests~=2.32.3`: HTTP requests to InfluxDB

### Development Dependencies
- `black~=24.4.2`: Code formatting
- `flake8~=7.1.1`: Linting with bugbear and black plugins
- `pytest`: Testing framework
- `pytest-mock`: Mock support for testing

## Configuration Schema

### Settings Structure (`settings.json`)
```json
{
  "hue": {
    "host": "hue.example.com",        // Hue bridge IP/hostname
    "user": "your_hue_user"           // Hue bridge username
  },
  "influx": {
    "url": "https://influx.example.com:8086",  // InfluxDB URL
    "db": "hue_db",                            // Database name
    "user": "your_influx_user",                // InfluxDB username
    "password": "your_influx_password",        // InfluxDB password
    "timeout": 5                               // Request timeout in seconds
  },
  "interval": 300,                    // Collection interval in seconds
  "temperature_units": "C",           // Temperature unit (C/F/K)
  "sensors": {                        // Name mappings for custom naming
    "Hue ambient light sensor 1": "Room1_Light_Sensor",
    "Hue temperature sensor 1": "Room1_Temperature_Sensor"
  }
}
```

## Data Processing Details

### Supported Sensor Types
- **ZLLTemperature**: Temperature sensors (converted to C/F/K)
- **ZLLLightLevel**: Light level sensors (converted to lux)
- **ZLLPresence**: Motion/presence sensors (converted to 0/1)

### Light Processing
- Dimmable lights: Brightness converted to percentage (0-100)
- Non-dimmable lights/smart plugs: Boolean on/off (0/1)

### Data Format
- InfluxDB line protocol: `hue,host=<bridge_host> <key>=<value>,<key>=<value>`
- Timestamp precision: seconds
- Host tag: Hue bridge hostname for data source identification

## Common Tasks

### Adding New Sensor Types
1. Identify the sensor type in Hue API response
2. Add processing logic in `parse_data()` function
3. Handle unit conversions if needed
4. Add test cases for the new sensor type
5. Update documentation

### Modifying Data Format
1. Update the InfluxDB line protocol formatting in `send_data_to_influx()`
2. Ensure backward compatibility with existing data
3. Update tests to reflect new format
4. Document changes in configuration

### Debugging Issues
1. Use `--dump` mode to inspect raw Hue API data
2. Use `--print` mode to see processed data without sending to InfluxDB
3. Check configuration file syntax and values
4. Verify network connectivity to Hue bridge and InfluxDB
5. Review error messages and exit codes
6. Use pytest to isolate specific functionality

## Performance Considerations
- Use appropriate timeouts for network operations (default: 5 seconds)
- Implement efficient data structures for processing
- Consider rate limiting for InfluxDB writes
- Monitor memory usage for long-running processes
- Use the interval-based timing system to avoid drift

## Security Notes
- Store sensitive credentials in `settings.json` with appropriate file permissions
- Use HTTPS for InfluxDB connections in production
- Validate all input data before processing
- Avoid logging sensitive information
- Consider using environment variables for sensitive data in production

## CLI Usage
- `python huetoinflux.py`: Normal operation (send data to InfluxDB)
- `python huetoinflux.py --dump`: One-time data export (JSON format)
- `python huetoinflux.py --print`: Continuous monitoring (JSON output to console)

## Testing Strategy
- Unit tests for all functions with mocked dependencies
- Test error conditions and edge cases
- Test configuration validation
- Test data processing with various sensor types
- Test CLI argument parsing
- Test signal handling and graceful shutdown