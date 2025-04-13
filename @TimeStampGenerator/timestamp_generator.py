#!/usr/bin/env python3

import datetime

def get_current_timestamp():
    """
    Get the current date and time and return it in a formatted string.
    
    Returns:
        str: Formatted date and time string (YYYY-MM-DD HH:MM:SS)
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp

def get_date_for_changelog():
    """
    Get the current date formatted for changelog entries.
    
    Returns:
        str: Date formatted as YYYY-MM-DD
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    return date_str

def main():
    """
    Main function to get and display the current timestamp.
    """
    timestamp = get_current_timestamp()
    print(f"Current timestamp: {timestamp}")
    
    date_for_changelog = get_date_for_changelog()
    print(f"Date for changelog: {date_for_changelog}")

if __name__ == "__main__":
    main()
else:
    # When imported as a module, print a message indicating successful import
    print(f"Timestamp generator module imported successfully") 