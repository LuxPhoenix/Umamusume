# Umamusume Game Automation - Refactored Structure

## Overview
This is a completely refactored version of the Umamusume game automation with a clean, modular structure for easy maintenance and testing.

## Project Structure

```
steam_ver/
├── core/                          # Core data structures and constants
│   ├── __init__.py
│   ├── constants.py               # All game constants and magic numbers
│   └── models.py                  # Data classes and enums
│
├── ui/                            # UI interaction modules
│   ├── __init__.py
│   ├── image_recognition.py      # Screen image detection
│   ├── click_handler.py           # Mouse click operations
│   └── window_manager.py          # Game window management
│
├── game_utils/                    # Utility modules
│   ├── __init__.py
│   ├── config_loader.py           # JSON configuration loading
│   ├── event_matcher.py           # Event text matching
│   └── screen_reader.py           # Screen text reading wrapper
│
├── events/                        # Game event handlers
│   ├── __init__.py
│   ├── event_handlers.py          # Special event handling
│   ├── mood_manager.py            # Character mood management
│   ├── health_manager.py          # Health/energy/infirmary checks
│   ├── race_manager.py            # Race operations and skill upgrades
│   └── training_manager.py        # Training selection and execution
│
├── control_laptop_new.py          # Main game controller
├── control_laptop.py              # Original file (keep for reference)
└── control_laptop_refactored.py  # Single-file refactored version
```

## Module Responsibilities

### core/
- **constants.py**: Contains all magic numbers, thresholds, wait times, and configuration values
- **models.py**: Data classes (Coordinate, WindowBounds) and enums (TrainingType, EventType, MoodLevel)

### ui/
- **image_recognition.py**: Screen image detection and recognition
- **click_handler.py**: All mouse click operations
- **window_manager.py**: Game window positioning and resizing

### game_utils/
- **config_loader.py**: Loading JSON configurations (dictionary, deck configs, support cards)
- **event_matcher.py**: Matching detected events to known events using WER
- **screen_reader.py**: Wrapper for screen text detection

### events/
- **event_handlers.py**: Handlers for special events, inspiration, new year, after-race events
- **mood_manager.py**: Checking and raising character mood
- **health_manager.py**: Infirmary checks and energy level management
- **race_manager.py**: Race finding, strategy changes, skill upgrades
- **training_manager.py**: Training option evaluation and selection

## Usage

### Basic Usage
```python
from control_laptop_new import UmaGame, resize_game

# Initialize game
resize_game()
game = UmaGame(test=True, deck_name="Cap")

# Start training loop
game.train_horse_loop(turn=1)
```

### Custom Character
```python
from horse_info import Oguri_Cap
from control_laptop_new import UmaGame

game = UmaGame(
    test=True,
    deck_name="Oguri",
    character=Oguri_Cap
)
game.train_horse_loop(turn=1)
```

### Manual Setup Creation
```python
game = UmaGame()
support_cards = ['Air Shakur (SSR)', 'Gold Ship (R)', 'Fine Motion (SSR)']
game.create_manual_setup(support_cards, deck_name="my_deck")
```

## Key Improvements

### 1. **Modularity**
- Each module has a single, well-defined responsibility
- Easy to test individual components
- Easy to modify without affecting other parts

### 2. **Type Safety**
- Comprehensive type hints throughout
- DataClasses for structured data
- Enums for fixed values

### 3. **Maintainability**
- Constants in one place
- No magic numbers in code
- Clear naming conventions
- Comprehensive docstrings

### 4. **Extensibility**
- Easy to add new event handlers
- Easy to add new training types
- Easy to add new race strategies

### 5. **Debugging**
- Centralized logging
- Clear error messages
- Structured exception handling

## Configuration Files

The automation uses JSON files in `data/json/`:
- `dictionary.json`: Main configuration with UI coordinates
- `{deck_name}.json`: Deck-specific event choices
- Support card data in `data/support_card_data/`

## Dependencies

```python
pyautogui       # Screen automation
pygetwindow     # Window management
jiwer           # Text similarity matching
```

Plus custom modules:
- `horse_info`: Character and support card definitions
- `utils.logger`: Logging configuration
- `utils.detect_text`: OCR text detection

## Migration from Old Code

To migrate from the old `control_laptop.py`:

1. **Import changes**:
   ```python
   # Old
   from control_laptop import UmaGame
   
   # New
   from control_laptop_new import UmaGame
   ```

2. **API remains compatible**: The main `UmaGame` class interface is unchanged
3. **New modular structure**: Can import specific managers for testing:
   ```python
   from events import MoodManager, TrainingManager
   from ui import ImageRecognition
   ```

## Testing

Each module can be tested independently:

```python
# Test image recognition
from ui import ImageRecognition
result = ImageRecognition.test_image("generaltraining/training")

# Test event matching
from game_utils import EventMatcher
match = EventMatcher.match_event("New Year's Gift", event_dict)

# Test window management
from ui import WindowManager
bounds = WindowManager.setup_game_window()
```

## Future Enhancements

Possible improvements:
- Add unit tests for each module
- Add configuration validation
- Add event recording/playback
- Add performance metrics
- Add multi-threading support
- Add GUI for configuration

## Notes

- Keep both old and new files during transition period
- Test thoroughly before removing old code
- Update any external scripts that import from control_laptop.py
- The refactored code maintains backward compatibility with the game API

## Support

For issues or questions:
1. Check module docstrings for detailed information
2. Review error logs in the logging output
3. Test individual modules in isolation
4. Refer to original control_laptop.py for behavior reference
