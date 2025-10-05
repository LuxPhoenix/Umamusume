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

# V0.3.8
An early stage of merging with laptop version in technology and style.
Major changes:
1. All files related to mobile version are moved under directory mobile_OS.
2. Addition of complete data from supportcards.
3. Refactoring and minor adjustments related to names of icons.
4. Improved mobile logic by minimizing chances of accidental training click.

Direction for V0.4:
1. Implementation of dictionary of icon coordinates, events, racetable, strategy, skill preferences.
2. Improving connecting logic to save time.
3. Making sure both laptop and mobile version could run smoothly.

Note: I was busy preparing for school exams last several weeks, and Coed did everything for the laptop (steam version), which is absolutely amazing. Now that I get back, I should devote more time into this project and make it better!

# V0.3.9
Implementation of scale adjusting mechanism: _detect_scale, _fp; testing mechanism: wait_for, wait_for_any, clicks_until.

First implementation ensures the scales between logical and actual pixel coordinates are adjusted on any screen. Second implementation saves time by clicking icons immediately upon occurance, and reduces risks of raising errors by waiting for connecting times. Team trial improved speed by 3 folds, training by 2 folds. 

Minor change in logics:
1. Team trial will run until no RP, and will not start running if no RP in the first place (instead of always run 5 times).
2. During training, training for any option won't trigger if no energy.
3. check_race and check_race_main are both accelerated, I do note that the end of check_race_main requires improvement.

# V0.4.0
This should mark a major leap towards functionality, unfortunately it's 4am and I gotta sleep, so no fancy summary.

Major changes:
1. Improvement in check race & check race main by fixing ending bugs and distinguishing URA final out of other races.
2. Inclusion of hints in score calculation, adding changable hint priority (could be adjusted different to suit parent & ace & debuffer & team trial & fan farming).
3. Improvement in trouble shooting by changing logical order and inclusion of "Cancel" button detection.
4. More addition of support card information and corresponding images.

Minor changes:
1. Relationship calculation made more exact in wording.
2. Sorting horse_info_m.json with name corrections.

# V0.4.1
This is an intermediate version aiming at bug fixes and semi-implementation of hint-value & training value calculation.

Major changes:
1. Addition of all races information beyond and including G3.
2. Implementation of trying again after failing goals.
3. Update the start game function to enable customized parent selection.
4. Update the mood related functions to make it safer.

Minor changes:
1. Restrict regions for previously unrestricted testing images, improving efficiency.
3. Fixing name issue for characters.
4. Reducing time taken for trouble shooting process.

# V0.4.2
Huge update to the skill system!

Major update agenda:

1. Collect skills available from hints and events (separately) for each support card.
--> All information together with skills are gathered for all SSR, SR and a few R cards.
--> Need to check the veracity for some values later, especially event skills.

2. Collect skills needed for each CM cup
--> Collected skills needed for Cancer cup front runners.
--> Need to replenish other running styles and other cups.

3. Write a class method for skills so each skill will have the following property: description, distance, strategy, usefulness (good skill like swinging maestro vs bad skill like iron will)
--> Skipped, I don't think this is necessary. If needed skills are already appended to
the CM, then we don't need to compare anymore.

4. Talk with Coed about the events from each support cards, and which choice to select to get which skill.


5. Add initial skills, initial aptitudes for each umamusume.
--> Added for existing Umas.

6. Write a function or method that could find useful skills out of the initial skills and support cards' skills for a certain scenario (If the horse is trained for CM, then prioritize CM's skills; debuffer; team trial; regular training (select skills based on initial aptitudes for the horse).)
--> Implemented hashable class "Skill" under support_card_m.py.
--> Added "load" method under horse_info_m.py, which will change the priority of skills based on scenerio (like CM cups) and change the overall priority to pick up hints based on training purposes.

7. When training, refine the hint detecting function so that we will know which exact card has the hint.
--> Implemented by pixel testing
--> Needs to find better testing technique to increase accuracy or adjust pixel collecitng position & multiple pixel collecting.

8. Add a score function for the hint of a particular support card
hint_priority = sum(usefulskill[i].importance) / number_of_available_hints * (1+ A*hint_levels) 
--> Implemented, need to fine tune the value.

9. Add a function to detect if a skill has already been obtained at certain turns.
So for instance if groundwork already is obtained, then we no longer need this hint from airgroove so it will be removed from air groove's useful skill list
Same with standard distance from Eishin Flash
So the result is that if we find we have picked up those two skills, we no longer care about hints from Air groove and Eishin Flash
This will increase efficiency so we can prioritize on stats gaining and also obtaining hints for other needed skills.
--> Function Added to detect available skills

10. Implement a function that ranks available skills in terms of priority, and pick skills in the most efficient way with limited skill points. the goal is to always pick skills at higher priority level. but with skills on the same level, we should try to spend our points on as much skills as possible and leave as fewer skill points as possible.

