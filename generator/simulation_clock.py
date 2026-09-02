# -*- coding: utf-8 -*-
"""
Simulation Calendar and Clock for FY 2025 in Morocco.
"""

from datetime import date, timedelta
from typing import List, Set, Dict


class SimulationClock:
    """
    Clock tracking daily business calendar, Moroccan public holidays,
    and statutory fiscal/social declaration deadlines for FY 2025.
    """

    MOROCCAN_HOLIDAYS_2025: Set[date] = {
        date(2025, 1, 1),    # Nouvel An civil
        date(2025, 1, 11),   # Manifeste de l'Indépendance
        date(2025, 1, 14),   # Nouvel An Amazigh
        date(2025, 3, 31),   # Aïd El Fitr (estimation 2025)
        date(2025, 4, 1),    # Aïd El Fitr 2ème jour
        date(2025, 5, 1),    # Fête du Travail
        date(2025, 6, 7),    # Aïd Al Adha
        date(2025, 6, 8),    # Aïd Al Adha 2ème jour
        date(2025, 6, 27),   # 1er Moharram (Nouvel An de l'Hégire)
        date(2025, 7, 30),   # Fête du Trône
        date(2025, 8, 14),   # Allégeance Oued Eddahab
        date(2025, 8, 20),   # Révolution du Roi et du Peuple
        date(2025, 8, 21),   # Fête de la Jeunesse
        date(2025, 9, 5),    # Aïd Al Mawlid Annabawi
        date(2025, 9, 6),    # Aïd Al Mawlid 2ème jour
        date(2025, 11, 6),   # Anniversaire de la Marche Verte
        date(2025, 11, 18),  # Fête de l'Indépendance
    }

    def __init__(self, year: int = 2025):
        self.year = year
        self.start_date = date(year, 1, 1)
        self.end_date = date(year, 12, 31)
        self.current_date = self.start_date

    def is_weekend(self, d: date) -> bool:
        # Saturday (5) or Sunday (6)
        return d.weekday() in (5, 6)

    def is_holiday(self, d: date) -> bool:
        return d in self.MOROCCAN_HOLIDAYS_2025

    def is_business_day(self, d: date) -> bool:
        return not self.is_weekend(d) and not self.is_holiday(d)

    def get_next_business_day(self, d: date) -> date:
        cur = d
        while not self.is_business_day(cur):
            cur += timedelta(days=1)
        return cur

    def get_all_days(self) -> List[date]:
        days = []
        cur = self.start_date
        while cur <= self.end_date:
            days.append(cur)
            cur += timedelta(days=1)
        return days

    def get_month_end_date(self, year: int, month: int) -> date:
        if month == 12:
            return date(year, 12, 31)
        next_month = date(year, month + 1, 1)
        return next_month - timedelta(days=1)

    def is_month_end(self, d: date) -> bool:
        return (d + timedelta(days=1)).month != d.month

    def is_quarter_end(self, d: date) -> bool:
        return (d.month in (3, 6, 9, 12)) and self.is_month_end(d)
