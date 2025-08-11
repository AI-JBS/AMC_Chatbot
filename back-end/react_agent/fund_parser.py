"""Helper functions for parsing fund names from user input."""

import re
from typing import List, Tuple

def extract_fund_names_from_text(text: str) -> List[str]:
    """Extract fund names from user text input.
    
    Args:
        text: User input text containing fund names
        
    Returns:
        List of extracted fund names
    """
    # Common fund name patterns
    patterns = [
        r'JBS\s+[A-Za-z\s]+Fund',  # JBS Alpha Growth Fund
        r'[A-Za-z\s]+Fund',         # Any text ending with Fund
        r'JBS\s+[A-Za-z\s]+',      # JBS followed by words
    ]
    
    found_funds = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = match.strip()
            if cleaned and cleaned not in found_funds:
                found_funds.append(cleaned)
    
    # Also try to extract by "and" separators
    if ' and ' in text.lower():
        parts = text.lower().split(' and ')
        for part in parts:
            # Look for fund-like words
            words = part.strip().split()
            if len(words) >= 2:
                potential_fund = ' '.join(words).title()
                if 'fund' in potential_fund.lower() or 'jbs' in potential_fund.lower():
                    found_funds.append(potential_fund)
    
    return found_funds[:2]  # Return max 2 funds for comparison

def parse_comparison_request(text: str) -> Tuple[str, str, str]:
    """Parse user request for fund comparison.
    
    Args:
        text: User input text
        
    Returns:
        Tuple of (fund1, fund2, metric)
    """
    # Extract fund names
    fund_names = extract_fund_names_from_text(text)
    
    # Default fund names if not found
    fund1 = fund_names[0] if len(fund_names) > 0 else "JBS Alpha Growth Fund"
    fund2 = fund_names[1] if len(fund_names) > 1 else "JBS Dedicated Equity Fund"
    
    # Extract metric
    metric = "365D"  # Default
    if "365d" in text.lower() or "365 d" in text.lower() or "year" in text.lower():
        metric = "365D"
    elif "expense" in text.lower() or "fee" in text.lower():
        metric = "Total Expense Ratio"
    elif "nav" in text.lower():
        metric = "NAV"
    elif "ytd" in text.lower():
        metric = "YTD"
    
    return fund1, fund2, metric