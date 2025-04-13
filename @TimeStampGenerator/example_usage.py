#!/usr/bin/env python3

# Import the timestamp generator module
import timestamp_generator

def update_changelog_example():
    """
    Example function demonstrating how to use the timestamp generator
    to update a changelog programmatically.
    """
    # Get formatted date for changelog entry
    date = timestamp_generator.get_date_for_changelog()
    
    # Get full timestamp for logging
    timestamp = timestamp_generator.get_current_timestamp()
    
    print(f"Updating changelog with date: {date}")
    print(f"Log entry created at: {timestamp}")
    
    # Example of how you might construct a changelog entry
    changelog_entry = f"""
## [1.5.0] - {date}

### Added
- New feature X
- Improved functionality Y

### Fixed
- Issue with Z
"""
    print("\nExample changelog entry:")
    print(changelog_entry)

if __name__ == "__main__":
    update_changelog_example() 