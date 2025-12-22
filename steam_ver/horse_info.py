"""
Horse girl character definitions.

REFACTORED: Now uses HorseService for creating characters.
This module provides convenient pre-configured character instances.
"""

from services import HorseService

# For backward compatibility, we still expose HorseGirl class
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.models import HorseGirl

# Pre-configured character instances
# These are created using HorseService which loads data from horse_info.json
Oguri_Cap = HorseService.create_horse_girl("Oguri Cap")
Daiwa_Scarlet = HorseService.create_horse_girl("Daiwa Scarlet")
Daiwa_Scarlet_2 = HorseService.create_horse_girl("Daiwa Scarlet 2")
Maruzensky = HorseService.create_horse_girl("Maruzensky")
El_Condor = HorseService.create_horse_girl("El_Condor")
Mayano_Top_Gun_Wedding = HorseService.create_horse_girl("Mayano Top Gun Wedding")
Maruzensky_2 = HorseService.create_horse_girl("Maruzensky 2")
Maruzensky_3 = HorseService.create_horse_girl("Maruzensky 3")
Maruzensky_4 = HorseService.create_horse_girl("Maruzensky 4")

# Export for backward compatibility
__all__ = [
    "HorseGirl",
    "Oguri_Cap",
    "Daiwa_Scarlet",
    "Daiwa_Scarlet_2",
    "Maruzensky",
    "El_Condor",
    "Mayano_Top_Gun_Wedding",
    "Maruzensky_2",
    "Maruzensky_3",
    "Maruzensky_4",
]
