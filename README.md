# breakthrough-playing-robot-arm
This project was my entry to a kind of science fair hosted by Testo in 2015
The entry consisted of a "uArm" robot arm that would autonomously play a game of "Breakthrough" against a human opponent.
The board state was detected using a webcam.
Competative Gameplay was enabled through implemention of Monte-Carlo simulation with a heuristic function being used after a certain depth of the game tree. 
Throughout the developement process, both ad-hoc and learned heuristic functions where created. 
In one instance, a neural network was evolved (through NEAT-python) using selfplay, which was used to evaluate game states.  
For the final presentation however, one of the ad-hoc heuristic functions was deemed best
The final agent could trade peaces quite well, however it was't as good at actually winning games.
