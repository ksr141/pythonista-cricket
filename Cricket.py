# coding: utf-8
 
import ui
import re
import console
 
# player object, tracks the marks made by each individual player
class Player(object):
	def __init__(self):
		# initialize all marks
		self.marks = [0]
		self.marks *= 26
		self.reset_board()
 
	# add a mark
	def add_mark(self, mark_num):
		self.marks[mark_num] += 1
	
	# sub a mark
	def sub_mark(self, mark_num):
		if self.marks[mark_num] > 0:
			self.marks[mark_num] -= 1
	
	# get the mark text based on current score
	def get_mark(self, mark_num):
		if   self.marks[mark_num] == 0:
			return ''
		elif self.marks[mark_num] == 1:
			return '/'
		elif self.marks[mark_num] == 2:
			return 'X'
		elif self.marks[mark_num] >= 3:
			return 'Ⓧ'
	
	# quick function to note if the given mark is closed
	def closed_mark(self, mark_num):
		return self.marks[mark_num] >= 3
 
	# start a new game
	def reset_board(self):
		for i in range(len(self.marks)):
			self.marks[i] = 0
 
 
# our main board oject, tracks the dart board
class Board(object):
	def __init__(self):
		# player objects
		self.players = [Player(), Player(), Player(), Player()]
		self.scores  = [0,0,0,0]
		# cut throat enabled
		self.cutthroat = True
		# max number of players
		self.max_players = 4
 
	# process the new dart mark
	def update_marks(self, player, mark_num, add_or_sub):
		# is this player active?
		if player > (self.max_players-1):
			return ''
		# subtract first before checking if the mark is closed
		if add_or_sub:
			self.players[player].sub_mark(mark_num)
			
		# if this mark is closed, update the scores
		if self.players[player].closed_mark(mark_num):
			if self.cutthroat:
				for i in range(self.max_players):
					if i != player and self.players[i].closed_mark(mark_num) == 0:
						if add_or_sub:
							self.scores[i] -= mark_num
							if self.scores[i] < 0:
								self.scores[i] = 0
						else:
							self.scores[i] += mark_num
			else:
				all_closed = True
				for i in range(self.max_players):
					if self.players[i].closed_mark(mark_num) == 0:
						all_closed = False
				
				if all_closed == False:
					if add_or_sub:
						self.scores[player] -= mark_num
						if self.scores[player] < 0:
							self.scores[player] = 0
					else:
						self.scores[player] += mark_num
 
		# add the new mark
		if add_or_sub == 0:
			self.players[player].add_mark(mark_num)
		
		# return the mark to display on the board
		return self.players[player].get_mark(mark_num)
	
	# check if somebody won
	def check_for_winner(self):
		# check 15-20
		for p in range(self.max_players):
			winner = True
			for i in range(15,21):
				if self.players[p].closed_mark(i) == 0:
					winner = False
			
			# closed all the numbers? how about bull and score
			if winner and self.players[p].closed_mark(25):
				for j in range(self.max_players):
					if       self.cutthroat and self.scores[p] > self.scores[j]:
						winner = False
					elif not self.cutthroat and self.scores[p] < self.scores[j]:
						winner = False
				if winner:
					return True, p
			else:
					winner = False
		
		return False, 0
		
	# return the score for a given player
	def get_player_score(self, player):
		if player > (self.max_players-1):
			return ''
		else:
			return str(self.scores[player])
	
	# update cut-throat status
	def update_cutthroat(self, new_value):
		self.cutthroat = new_value
	
	# update max number of players
	def update_maxplayers(self, new_value):
		self.max_players = new_value
	
	# reset the board
	def reset_board(self):
		for p in range(4):
			# reset each player object
			self.players[p].reset_board()
		# clear the scores
		self.scores = [0,0,0,0]
 
 
# allow popups while running
@ui.in_background
 
# executed on button press
def button_tapped(sender):
	# grab the player number and the space hit from the button name
	button = re.match(r'button_(\d+)_(\d+)', sender.name)
	
	# get the status of the plus/minus control
	seg_control   = sender.superview['plus_minus']
	add_or_sub = seg_control.selected_index
	
	# mark this as a hit and update the text displayed on the button
	sender.title = DartBoard.update_marks(int(button.group(1)), int(button.group(2)), add_or_sub)
 
	# update the scores
	for i in range(4):
		# grab the UI handle and update the score text
		t = sender.superview['score'+str(i)]
		t.text = DartBoard.get_player_score(i)
 
	# check if we can declare a winner
	won,player = DartBoard.check_for_winner()
	if won:
		t = sender.superview['textfield'+str(player)]
		response = console.alert('Game Over', t.text + ' Won!', 'Reset')
		
		# start a new game
		if response == 1:
			reset_board(sender)
			
			
# allow popups while running
@ui.in_background
 
# executed on reset button press
def reset_button_tapped(sender):
	# lets double check you really want to do this
	response = console.alert('WARNING', "Reset current game?", 'Yes')
	
	if response == 1:
		reset_board(sender)
 
# start a new game
def reset_board(sender):
	DartBoard.reset_board()
	
	# clear all the marks and scores
	for p in range(4):
		# clear the scores
		t = sender.superview['score'+str(p)]
		t.text = '0'
		# clear all the marks
		for m in range(15,21):
			t = sender.superview['button_'+str(p)+'_'+str(m)]
			t.title = ''
		# clear the bull marks
		t = sender.superview['button_'+str(p)+'_25']
		t.title = ''
 
 
# executed when the switch for cut throat changes
def cut_switch_changed(sender):
	DartBoard.update_cutthroat(sender.value)	
 
	# update label text
	t = sender.superview['cutthroat']
	if sender.value:
		t.text = 'Cut Throat'
	else:
		t.text = '  Regular'
 
 
# executed when the switch for max players changes
def player_switch_changed(sender):
	if sender.value:
		DartBoard.update_maxplayers(4)
	else:
		DartBoard.update_maxplayers(2)
 
	# update label text
	t = sender.superview['max_players']
	p3 = sender.superview['score2']
	p4 = sender.superview['score3']
	if sender.value:
		t.text = '4 Players'
		p3.text = DartBoard.get_player_score(2)
		p4.text = DartBoard.get_player_score(3)
	else:
		t.text = '2 Players'
		p3.text = ''
		p4.text = ''
 
 
# Main task, just build a new board object and load the UI
DartBoard = Board()
v = ui.load_view('Cricket')
if ui.get_screen_size()[1] >= 768:
	# iPad
	v.present('popover')
else:
	# iPhone
	v.present(orientations=['portrait'])

