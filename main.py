'''
Conway's Game of Life

'''
import sys
import random
import copy
import argparse
import os
import pygame as mygame
from pygame import Rect as rect

# Colours used (Python RGB format)
black = (0, 0, 0)
white = (255, 255, 255)
darkslategray = (47,79,99)

# Parser arguments
parser = argparse.ArgumentParser()
parser.add_argument("--scale", type=int, help="amount of pixels to equal one cell; will impact performance if set too low (default: 20)")
parser.add_argument("--window", help="size of window based on number of pixels, using the format WxH, e.g. 500x1000 (default: 1000x1000)")
parser.add_argument("--size", help="size of window based on number of cells, using the format XxY, e.g. 20x40 (auto-calculates width & height based on scale provided, or default)")
parser.add_argument("--framerate", type=int, help="maximum framerate (default: 60)")
parser.add_argument("--unlimited_framerate", action="store_true", help="disable framerate limiting")
parser.add_argument("--file", help="load cells from file")
args = parser.parse_args()


# Reset all squares
def reset_squares():
	for i in range(len(squares)):
		for j in range(len(squares[0])):
			squares[i][j] = False

# Generate random living squares
def generate_random(spawn_rate):
	for i in range(len(squares)):
		for j in range(len(squares[0])):
			squares[i][j] = not bool(random.randint(0, spawn_rate))

# Export cell array to txt file
def export(squares, scale, width, height):
	filename = "export.txt"
	
	# Delete save file if it already exists
	try:
		os.remove(filename)
	except OSError:
		pass
	
	with open(filename, "a") as f:
		f.write("%d|%d|%d\n" % (scale, width, height))
		for j in range(len(squares[0])):
			for i in range(len(squares)):
				f.write("1" if squares[i][j] else "0")
			f.write("\n")

# Inject game of life rules
def pro(squares):
	new_squares = copy.deepcopy(squares)
	for i in range(len(squares)):
		for j in range(len(squares[0])):
			num_neighbours = neighbours(squares, i, j)
			if squares[i][j] == True and num_neighbours != 2 and num_neighbours != 3:
				new_squares[i][j] = False
			if num_neighbours == 3 and not squares[i][j]:
				new_squares[i][j] = True
	return new_squares

# Simulates the neighbour's behaviour based on the rules
def neighbours(squares, i, j):
	n = 0
	if i - 1 >= 0 and j - 1 >= 0 and squares[i - 1][j - 1] :
		n += 1
	if j - 1 >= 0 and squares[i][j - 1]:
		n += 1
	if i + 1 < len(squares) and j - 1 >= 0 and squares[i + 1][j - 1]:
		n += 1
	if i + 1 < len(squares) and squares[i + 1][j]:
		n += 1
	if i + 1 < len(squares) and j + 1 < len(squares[0]) and squares[i + 1][j + 1]:
		n += 1
	if j + 1 < len(squares[0]) and squares[i][j + 1]:
		n += 1
	if i - 1 >= 0 and j + 1 < len(squares[0]) and squares[i - 1][j + 1]:
		n += 1
	if i - 1 >= 0 and squares[i - 1][j]:
		n += 1
	return n


# Game settings (Change to your liking)
scale = args.scale or 20
width = 800
height = 600
framerate = args.framerate or 60
unlimited_framerate = args.unlimited_framerate

mygame.init()

caption_init = "Conway's Game of Life - "
mygame.display.set_caption("Conway's Game of Life")
clock  = mygame.time.Clock()

# Set width and height based on specified size
if args.window:
	width = int(args.window.split("x")[0])
	height = int(args.window.split("x")[1])

# Verify width and height are divisible by the scale factor
if width % scale or height % scale:
	sys.exit("Width and/or height are not divisible by the scale factor")

# Set width and height based on specified number of cells in x and y
if args.size:
	width = int(args.size.split("x")[0]) * scale
	height = int(args.size.split("x")[1]) * scale

# Process loading file parameters
if args.file:
	with open(args.file, "r") as f:
		file_lines = f.readlines()
	
	file_arguments = file_lines[0].split("|")
	scale = int(file_arguments[0])
	width = int(file_arguments[1])
	height = int(file_arguments[2])

	file_lines = file_lines[1:]


# Number of cells in the x and y directions
num_x = int(width / scale)
num_y = int(height / scale)

# Game state
squares = [ [0] * num_y for _ in range(num_x)]

# Import cells if loading from save file
if args.file:
	for i in range(len(file_lines)):
		for j in range(len(file_lines[0])):
			if file_lines[i][j] == "\n": continue
			squares[j][i] = bool(int(file_lines[i][j]))

# Squares for the quick save
saved_squares = [ [0] * num_y for _ in range(num_x)]

# Inject the screen surface
screen = mygame.display.set_mode((width, height))

# Game variables
simulate = False
speed = 1
frame = 0
gridlines = True

# Main loop processed each frame
while True:
	frame += 1

	# Event listener processes the player's inputs
	for event in mygame.event.get():
		if event.type == mygame.QUIT: sys.exit()
		
		if event.type == mygame.KEYDOWN:
			# Play/pause the game
			if event.key == mygame.K_SPACE:
				simulate = not simulate
			
			# Decreases the game speed
			if event.key == mygame.K_MINUS or event.key == mygame.K_KP_MINUS:
				speed = 2 * speed

			# Increases the game speed
			if event.key == mygame.K_EQUALS or event.key == mygame.K_KP_PLUS:
				if speed > 1:
					speed = speed / 2
				else:
					speed = 1

			# Resets game speed to default (1)
			if event.key == mygame.K_1:
				speed = 1

			# Clears all squares
			if event.key == mygame.K_c:
				reset_squares()

			# Generates random squares
			if event.key == mygame.K_r:
				generate_random(5)

			# Toggles gridlines
			if event.key == mygame.K_g:
				gridlines = not gridlines
			
			# Saves the game state
			if event.key == mygame.K_s:
				saved_squares = copy.deepcopy(squares)

			# Loads the saved game state
			if event.key == mygame.K_l:
				squares = copy.deepcopy(saved_squares)

			# Exports the game state to a .txt file
			if event.key == mygame.K_e:
				export(squares, scale, width, height)

			# Shows the next frame of the game
			if event.key == mygame.K_n:
				squares = pro(squares)
			
			# Quits the game
			if event.key == mygame.K_ESCAPE:
				sys.exit()

	# Gets the current mouse position
	mouse_pos = mygame.mouse.get_pos()
	
	# Adds a cell when left clicked
	if mygame.mouse.get_pressed()[0]:
		i = int(mouse_pos[0] / scale)
		j = int(mouse_pos[1] / scale)
		squares[i][j] = True
	
	# Removes the cell when it is right clicked
	if mygame.mouse.get_pressed()[2]:
		i = int(mouse_pos[0] / scale)
		j = int(mouse_pos[1] / scale)
		squares[i][j] = False
	
	# Fills screen with a colour (Add your own if you like) 
	screen.fill(darkslategray)

	# Draw gridlines on screen
	if gridlines:
		for i in range(len(squares) + 1):
			mygame.draw.line(screen, white, (i * scale, 0), (i * scale, height))
		for i in range(len(squares[0]) + 1):
			mygame.draw.line(screen, white, (0, i * scale), (width, i * scale))

	# Draw squares on screen
	for i in range(len(squares)):
		for j in range(len(squares[0])):
			if squares[i][j]:
				mygame.draw.rect(screen, black, rect(i * scale, j * scale, scale, scale))
	
	# Simulate the injected rules
	if simulate:
		if frame % speed == 0:
			squares = pro(squares)

	# Update title bar with game stats
	caption = caption_init + "Speed: 1/%d,  %s" % (speed, "Playing" if simulate else "Paused")
	mygame.display.set_caption(caption)

	# Highlights selected cell(s)
	if not simulate:
		i = int(mouse_pos[0] / scale)
		j = int(mouse_pos[1] / scale)
		if squares[i][j]:
			mygame.draw.rect(screen, black, rect(int(mouse_pos[0] / scale) * scale, int(mouse_pos[1] / scale) * scale, scale, scale))
		else:
		    mygame.draw.rect(screen, black, rect(int(mouse_pos[0] / scale) * scale, int(mouse_pos[1] / scale) * scale, scale, scale))
	
  
	mygame.display.flip()