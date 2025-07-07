# Umamusume
This is a project aiming at automatically running the game of Umamusume Pretty Derby. 

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


