# Semiosphere
A Strategy Game created by Zach Dugger and programmed by Forrest Pruitt.

## Running Semiosphere

* install python3
* clone repo or download zip (https://github.com/fpruitt/semiosphere/archive/master.zip)
* run `python3 game.py` to start the game, in the unzipped file above.

## Quick install + run script for OSX
I know not everyone is a terminal/git/build-from-source wizard, so here's a simple script for OSX to get the prerequisites installed, along with the game. Simply copy and paste the lines below into your terminal (you'll have to give your password after the second line to install python3) and you should have the game running in no time! (Note: to open the terminal, type command-space to open spotlight, then type 'terminal' and hit enter)
```
curl https://www.python.org/ftp/python/3.4.4/python-3.4.4-macosx10.6.pkg >> ~/Downloads/python3.pkg
sudo installer -pkg ~/Downloads/python3.pkg -target /
curl -Lk https://github.com/fpruitt/semiosphere/archive/master.zip >> ~/Downloads/semiosphere.zip
unzip ~/Downloads/semiosphere
cd ~/Downloads/semiosphere-master
python3 game.py
```

### Running the game after the above script installs
To play Semiosphere after the first install, copy the below into a terminal:
```
cd ~/Downloads/semiosphere-master
python3 game.py
```


## Info and Rules
Note: This game is a work in progress. These rules are subject to, and probably will, change.

### Object
The object of the game is to reach the Semiosphere (the back row) with your planet intact. 

### Actions & Movement
Each player gets three action points per turn. Players can move forward (towards the Semiosphere), backwards, and laterally.
The number of action points required for a given action is shown in the action choice menu.

### The Void
At the end of a round, when all players have completed their turn, 'The Void' encroaches on the bottom-most non-voided row.
Any players in this row automatically lose the game. Any marks in the row that is taken give the players they belong to an additional move per mark.
Any planets that are in this row are lost forever.

### Marks
Players can use their points to create 'marks'.
Players cannot travel over thier opponents' marks, and must use action points to erase them or go around them in order to advance.
Players can travel over their own marks.
When The Void encroaches on the row that a mark is in, the player who laid down that mark gets an extra action on their next turn.
This stacks-- muliple marks in the row that was taken means multiple points!

### Dropping Your Planet
Players can 'drop' their planet onto the square behind them. This action costs one point and automatically awards two points.
As long as the planet is dropped, you gain +2 action points a turn-- but be careful, in order to win the game, you need to cross into the Semiosphere holding your planet!
It's important to note that you can only interact with your planet once per turn; it cannot be dropped on the turn you pick it up, and vice-versa.
You can drop your planet on a cell with your own mark, but not one with another player's mark.

### Recovering Your Planet
To recover your planet, all you need to do is enter the cell that it is currently sitting in.
You can't do this on the same turn that you have dropped it.

### Losing Your Planet
If you cannot recover your planet before it is lost to the void, it is gone for good. 
You still get the +2 move bonus, but you cannot win automatically just by crossing into the Semiosphere.
If you've lost your planet, your only hope of winning is by ensuring no other players cross the threshold with their planets before the void takes them.

### Crossing into the Semiosphere
You need 5 action points to cross into the Semiosphere. If you are currently holding your planet and you cross the threshold, the game ends and you win.
If you cross the threshold but do not have your planet you do not win automatically, but you can stay in the Semiosphere.
While in the Semiosphere, you take your turns like normal, but instead of using actions for movement, you can focus all of your attention on 
stopping the other players from reaching their goal!

### Leaving the Semiosphere
You can leave the Semiosphere, so long as The Void hasn't taken the final row.
You will pay the same cost (5 action points) to re-enter it later.
When you exit, you are placed onto the row closest to the semiosphere. 
You choose the column you wish to exit onto.

### Tieing
If multiple players reach the Semiosphere and none of them have their planets by the time the Void takes all of the rows or their planets, the game ends in a tie between those players.
