# Arcade
## What is this?
The goal of this is to provide an example of what to do (or don't as you see fit) in creating a collection of standalone games using [state](https://en.wikipedia.org/wiki/State_pattern) and [Observer](https://en.wikipedia.org/wiki/Observer_pattern) patterns. The idea sprang up from the discontinuation of [Brain Station](https://l-works.net/brainstation.php) and thus the framework is aimed at fulfilling this goal, but it should be flexible enough to allow one to make whatever they please.
## Is this stable?
In a manner of speaking, yes. There should not be anymore breaking changes to the code. Though the contents of files may alter, I will try and preserve any old functions in order to maintain compatibility. Should a change occur, I will do my best to provide ample warnings before removing old code
## How do I run this?
You need at least [Python 3.10](https://www.python.org/downloads/). After that, the steps are as expected, that is:
```
$git clone https://github.com/Amerikranian/Arcade
$cd Arcade
$pip install -r requirements.txt
```
If you are planning to contribute, then change the last line to install `requirements-dev.txt`, like so
```
$pip install -r requirements-dev.txt
```
## What is left?
- Adding some semblance of word complexity, perhaps based on Scrabble rules
- Adding graceful cleanup upon application errors
- Figuring out a way to unlock games (A shop? Achievements? Something that functions as a mix of the two?)
- Writing a CLI tool that can modify game JSON
- Actually writing games
## What is the general game development workflow?
Game additions occur in three steps
1. Adding game definitions to info.json within *data/games* directory
2. Creating the respective file within the *games* directory. Your game's class name must match the created JSON key! Your class must also take exactly two arguments, game variation and difficulty
3. Importing the game into `__init__.py` of the *games* directory. Said import must result in the actual class being accessible within the games module.
### A sample game
#### JSON
Since we currently lack the ability to unlock games, below is the simplest definition you could have for your game. Said definition must be pasted within info.json under *games* key.
```JSON
"SampleGame": {
    "unlocked_by_default": true
}
```
#### Game code
Create a file within the games directory with any desired name and populate it like so:
```python
from .base_game import Game


class SampleGame(Game):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        # Your code below
```
Keep in mind that you have access to the entirety of the methods within the Screen class. If you wish to use the ObservableGame class, the procedure is almost identical
```python
from .observable_game import ObservableGame, GameObserver


class SampleGame(ObservableGame):

def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(YourObserver())


class YourObserver(GameObserver):

    def __init__(self):
        super().__init__()
        # More code below
```
See GameObserver class for more details
#### Adding the game to the games module
modify `__init__.py` in the games directory by adding this line
```python
from .your_sample_game_filename import SampleGame
```
### The end
Regardless of what method you chose (working with the game class directly or using observers) you should be able to play your game now. Look in constants.py to see what kind of data you can alter about the SampleGame, and check out Hangman for a longer observer-oriented example
## What games do you have planned?
- Word Builder
- Word Search
- And probably some more as I work on this
## Can I help?
Sure. Pull requests and suggestions are welcomed. Discussion is encouraged. Like I said, half of this is me figuring it out. I would appreciate opening issues before opening pull requests. Said requests must also be properly formatted (use black).
## Wait... no typing?
Typing will be added... eventually. Bare with me, please.
## Wait... Where are the docs!
If there is enough interest I will move them up in priority, but due to having very limited time and no idea if anyone is interested in this they are very sparse.
