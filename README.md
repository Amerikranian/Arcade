# Arcade
## What is this?
The goal of this is to provide an example of what to do (or don't as you see fit) in creating a collection of standalone games using [state](https://en.wikipedia.org/wiki/State_pattern) and [Observer](https://en.wikipedia.org/wiki/Observer_pattern) patterns. The idea sprang up from the discontinuation of [Brain Station](https://l-works.net/brainstation.php) and thus the framework is aimed at fulfilling this goal, but it should be flexible enough to allow one to make whatever they please.
## Is this stable?
Until some games have been made (I am still in the preliminary stage of figuring out how everything is going to work) expect things to change as I run into unexpected problems. In particular, games are still iffy, relying on the observer model and lacking the ability to modify state stack. This is not an issue for word games but may be a problem for something a bit more complex.
## What is left?
- Writing a parser for game data and thereby implementing saving / loading
- Adding a way to keep track of game statistics split by variation and difficulty
- Adding sound support, probably in the form of an observer
- Actually writing games
## What about sounds?
Since this is an experiment, I do not think that an official set of sounds is going to be provided here. However, I do intend to eventually provide a sound backend so users can just add sounds  and play them with minimal effort.
## What about actually having a list of words?
I wrote a script to scrape [Merriam Webster's Dictionary](https://www.merriam-webster.com/). I can't guarantee how, uh, up to date the words we get are because some of them are quite strange, but it will do. I will eventually add the word list as a db which users can query with [sqlite3](https://docs.python.org/3/library/sqlite3.html)
## What games do you have planned?
- Anagrams
- Hangman
- Jotto
- Word Builder
- Word Search
- And probably some more as I work on this
## Can I help?
Sure. Pull requests and suggestions are welcomed. Discussion is encouraged. Like I said, half of this is me figuring it out. You can suggest games even, but I would wait to do so until I cement how this all is going to work
## Wait... no typing?
Typing will be added... eventually. Bare with me, please.
## Wait... Where are the docs!
If there is enough interest I will move them up in priority, but due to having very limited time and no idea if anyone is interested in this they are very sparse.