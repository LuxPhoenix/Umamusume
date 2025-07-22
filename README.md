# Umamusume
This is a project aiming at automatically running the game of Umamusume Pretty Derby. 

I will now include instructions about how you could run this code on your macbook:

1. Make sure you have python installed. You can install from homebrew, from official website of python, from anaconda, or any other ways you want.

2. It is recommended for you to download visual studio code, which is a really convenient platform for coding. 


# V0.1
For this early draft I just created a function control.start_game, which takes a bool parameter and will start the game from home screen of umamusume pretty derby international edition. If it takes zero, a new game is started. If the parameter is one, then it continues a previous save.

This version unfortunately only works on my macbook with screen size 2880 * 1864.

To run this code you need to install pyautogui, pillow, and OpenCV

On macbook I used iphone mirroring to connect to mobile device and then run this code. The window do have to be fixed to the top right corner of the macbook.

I know this code is insanely bad but trust me it is only starting.

# V0.2
I implemented functions to adjust the coordinate system based on the position and size of the game window. This allows the game window to be placed anywhere in the screen (the entire game window must not be covered, or else it will fail to detect icons.) Note: during gameplay the window cannot be moved. (In the future I will add a update function called whenever the window is moved.)

All functions except for image identification and clicking are integrated into class Umagame.
The clicking method will adjust the coordinate of clicking based on the relative position of the player's window. clicking_image is a method that accurately clicks the true position of image, which makes sense as its true position, rather than relative position, is identified via pyautogui.

I made two internal methods: _start_game(mode: bool) and _team_trial().
Hopefully I could integrate them together later by adding functions detecting energy.

# V0.2.5
I implemented training algorithms but it's only half finished and have not been tested. I need to add more images, change names, and complete not implemented areas, as well as internal methods of adjusting mood and training. I also need to add function about inheriting event and URA Finale event. It's a long day for me and I will take a short break. 

Mon 7 July

# V0.2.8
I added training logic, rest logic, infirmary logic, multiple choice logic, recover mood logic. Training logic is not complete yet, as I only let her click on speed training only. However I was able to pass URA with this code.

# V0.2.9
Inheritanting event logic added. Training algorithm half completed (counting number of heads for each training option, as well as the mood score).

TD: add friendship training detection and integrate it into score counting.
Have not been tested.

# V0.3.0
Finally, this is a version where the program could run the game completely, from selecting character, parents, friend support card, and then play the game.
The training logic is based on counting calculating scores for each training options as well as recover mood. URA finale logic is added, the energy detection is improved, and restrictions on area of scanning for certain parts have reduced the cost. This version runs the game slowly though, as it is to ensure the training loop will not skip some of its logic while the page loads or dialog piles over the page. Using this version I was able to consistently pass URA finale, obtain around 220,000 fans, and get a B+ rating Umamusume.

The focuse for versions of 0.3 will be the follow four ideas:

1. Implementing logic based on turns. (for instance prioritizing rest before summer training, attend certain G1 races to meet fans number requirements or just for attending.)

2. Add default support cards and event calender for different Umamusume, as well as special events of characters and support cards.

3. Reduce time needed for training by completing image scanning restrictions, reduce time.sleep as much as possible.

4. Implement detection of TP and RP and act accordingly to conduct team trials and training automatically.

# V0.3.1

Implementation of race functions (will select required race to attend at turns included in racelist for the character), multiple bug fixes (connection error, stuck on next page, and closing insufficient fan number pop-up), refining turn logic.

To do: refine race and main race function. For race function, replace the trouble shoot logic to scroll down the race list to find out required race. For main race, add algorithm to retry when failing to meet goal condition.

Result: This version of code is able to produce rank A Oguri Cup with 350k+ fans.

# V0.3.5
Major update! I just implemented functions to test for the relationship bar for supportcards during training, which will allow rainbow training to be detected. Upon this mechanism the score function is made better. For each support card, it's score contributed to a training type will be:

If the card is not present under the training type, then score is 0.
        
The score is 1 if this card is present and the relationship bar is not organge yet, since it is valuable to
increase the relationship.
        
The score is 2.4 if relationship bar is organge & maxed, and the support card is present under its specialized
training type. This triggers friendship traininng, which is immensely valuable.
        
The score is 0.6 if relationship is organge & maxed but rainbow training is not triggered. This mearly addes up the 
training effectiveness & mood bonus, so the benefit is smaller.

I also made changes to the _check_training function to make it more efficient, now it takes about 1/3 less time to operate than before.

Data related to horsegirls and supportcards are recorded in json files, and I made two corresponding class for them.
I also improved the _check_race function, which is now functioning normally.

Lastly, the team-trial function is made faster by simply fast-clicking on next (which is simple but efficient).

# V0.3.6
Improvement on support card relationship detection: original method of locating organe bar has low accuracy due to limits of pyautogui, so it is replaced by testing the color of a single pixel in the relationship bar. Now rainbow detection is highly accurate. Only limit is the support card pictures need to be taken exactly at the same position (otherwise the corresponding pixel tested for relationship may not lie in the relationship bar.)