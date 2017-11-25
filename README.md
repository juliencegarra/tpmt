

<h1>The TimePressureMazeTask (TMPT)</h1> The TMPT was coded by Julien Cegarra (Prof. in Cognitive Ergonomics/Psychology) for the <a href="https://www.univ-jfc.fr/equipesrecherche/sciences-la-cognition-technologie-ergonomie-scote">Cognition Sciences, Technology, Ergonomics (SCoTE) Laboratory</a>, Albi, France. This program allows to study in a unique task both time estimation and time production, which is a topic of interest in Psychology.
<br><br>
Contact for the program: julien.cegarra AT univ-jfc.fr
<br><br>
In this task, participants have to solve a series of mazes. The maze's start position is always on the lefthand side of the screen, and the finish position always on the righthand side.
To move through the maze from start to finish, participants have to move the character using the arrow keys of the keyboard.
The program stops when participants find a magic fruit on their path, which appear at the end of one of the three target durations (30 s, 60 s or 90 s).

Time pressure is induced by a ghost that haunts the participant’s character. More specifically, the ghost move faster and is closer to the participant’s
character in the condition with time pressure than in the condition without time pressure, but is never able to catch the character up. 

In this task, the participant has to solve three different mazes for three different duration (short (30 s), medium (60 s) and long (90 s)), making a total of nine mazes. 
We also include three mazes in which participants are always caught up by the ghost and therefore fail to solve the maze.
All the mazes have exactly the same number of wrong paths with identical features, so that the level of difficulty is similar, regardless of the
resolution duration.
Moreover, the mazes are displayed in a fog, where only the area around the participant's character and the ghost is illuminated. This way, participants have no visual
clues about the maze’s length.

(for more details for the scientific aspect see: <i>Rattat, A.-C., Matha, P., & Cegarra, J. (submitted). Time flies faster under time pressure</i>). 
<br><br>
<center><img src="https://github.com/juliencegarra/tpmt/blob/master/example.gif?raw=true"></center>
<br><br>
The program requires Python 2.x (tested on version 2.7) and the corresponding version of the Pygame library, freely available online. Make sure you install the matching (32- or 64-bit) version of Pygame as your Python installation, and the one compatible with your Python version number.  The program was coded for Windows systems. Some minimal code update will be necessary to run under linux or mac (especially to consider the difference in file systems).

Graphics were done by David Reilly. They are free to use. The porkys font is copyrighted by Fontalicious ( https://www.dafont.com/fr/porkys.font ). This font is free to use for personal usage.

The program is licenced under a MIT licence. 





<h2>Running the TPMT</h2>

To test the TPMT just download all the files and run “mtpt.py”.

At the end of the task, if a “results” directory does not exist it will be created in the same directory. Then for each participant a subdirectory will be created and it will include all of their data. Saved data is in a .csv file format that you can directly open in MS Office, OpenOffice or LibreOffice. Saved data will include
<ul><li>Participant information (firstname, age, sex and the last 4 numbers of phone number for identification reason).</li>
<li>Time estimation (or time production) of maze duration by participants</li>
<li>All behavioral traces with a msec. timestamp (key press, movements in maze, movements of the ghost, actions such as the capture of a fruit and so on).</li>
</ul>

<h2>Modifying the TPMT</h2>

The TPMT was written to be easily modifiable by means of text files. The game functioning is organized around different files containing either:
<ul><li>A List of mazes (“<a href="https://github.com/juliencegarra/tpmt/blob/master/res/_listtrainingfiles.txt">_listtrainingfiles.txt</a>“ for those used in the training phase; “_listescenariosfiles.txt” for those in the experiment itself)</li>
<li>Mazes. Their time reference is 30, 60 or 90 seconds. In order to define their duration, their filename must contain “short”, “medium” or long respectively. If the trial requires the participant to fail (ie. the ghost will eat the participant), just include “fail” in the filename. Examples: <a href="https://github.com/juliencegarra/tpmt/blob/master/res/Medium-2A.txt">Medium-2A.txt</a> <a href="https://github.com/juliencegarra/tpmt/blob/master/res/Long-fail.txt">Long-fail.txt</a> </li>
<li>Instructions to display before or after a maze. The instructions provided are currently in French.</li>
</ul>
The code itself is a bit rough but easily customizable. It contains undocumented capability of displaying rating scales. Overall the code will probably support a bit of refactoring in different files.

When the participant indicate his/her data, he/she will also be requested a scenario ID (that the experimenter will give to him/her). There are 8 different scenarios types which allow to provide different variant of the task:
<table>
<tr><td>Scenario ID</td><td>Task type</td><td>Time pressure</td><td>dial/clock visible</td></tr>
<tr><td>a</td><td>estimation</td><td>yes</td><td>no</td></tr>
<tr><td>b</td><td>estimation</td><td>no</td><td>no</td></tr>
<tr><td>c</td><td>estimation</td><td>yes</td><td>yes</td></tr>
<tr><td>d</td><td>estimation</td><td>no</td><td>yes</td></tr>
<tr><td>e</td><td>production</td><td>yes</td><td>no</td></tr>
<tr><td>f</td><td>production</td><td>no</td><td>no</td></tr>
<tr><td>g</td><td>production</td><td>yes</td><td>yes</td></tr>
<tr><td>h</td><td>production</td><td>no</td><td>yes</td></tr>
<tr><td>i</td><td>prospective</td><td>yes</td><td>no</td></tr>
<tr><td>j</td><td>prospective</td><td>no</td><td>no</td></tr>
<tr><td>k</td><td>prospective</td><td>yes</td><td>yes</td></tr>
<tr><td>l</td><td>prospective</td><td>no</td><td>yes</td></tr>
</table>
