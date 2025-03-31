"""
Handler for date calculation questions.
"""

from datetime import datetime, timedelta
from typing import Tuple, List


class DateHandler:
    """Handler for questions involving date calculations."""
    
    async def count_wednesdays(self, start_date_str: str, end_date_str: str) -> str:
        """
        Count the number of Wednesdays between two dates (inclusive).
        
        Args:
            start_date_str: Start date in YYYY-MM-DD format
            end_date_str: End date in YYYY-MM-DD format
            
        Returns:
            The count of Wednesdays as a string
        """
        try:
            # Parse dates
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Initialize counter
            count = 0
            
            # Iterate through each day
            current = start_date
            while current <= end_date:
                if current.weekday() == 2:  # Wednesday is 2 in Python's weekday()
                    count += 1
                current += timedelta(days=1)
            
            return str(count)
        
        except ValueError:
            # Try alternative date formats
            try:
                # Try MM/DD/YYYY format
                start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
                end_date = datetime.strptime(end_date_str, "%m/%d/%Y")
                
                # Continue with the same logic as above
                count = 0
                current = start_date
                while current <= end_date:
                    if current.weekday() == 2:
                        count += 1
                    current += timedelta(days=1)
                
                return str(count)
            
            except Exception as e:
                return f"Error parsing dates: {str(e)}. Please use YYYY-MM-DD format."
        
        except Exception as e:
            return f"Error counting Wednesdays: {str(e)}"
    
    async def date_diff(self, date1_str: str, date2_str: str) -> str:
        """
        Calculate the difference between two dates in days.
        
        Args:
            date1_str: First date in YYYY-MM-DD format
            date2_str: Second date in YYYY-MM-DD format
            
        Returns:
            The difference in days as a string
        """
        try:
            date1 = datetime.strptime(date1_str, "%Y-%m-%d")
            date2 = datetime.strptime(date2_str, "%Y-%m-%d")
            
            diff = abs((date2 - date1).days)
            return str(diff)
        
        except Exception as e:
            return f"Error calculating date difference: {str(e)}"