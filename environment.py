#Backend environment of the game
#Lógica necessária para jogabilidade

from copy import deepcopy


# number of rows/cols = BOARD_SIZE - 1
BOARD_SIZE = 20 


#the opposite color to the one provided.
def opponent_color(color):

    if color == 'WHITE':
        return 'BLACK'
    
    elif color == 'BLACK':
        return 'WHITE'
    
    else:
        print('Invalid color: ' + color)
        return KeyError
    



#List of neighboring points
def neighbors(point):

    neighborhood = [(point[0] - 1, point[1]),
                   (point[0] + 1, point[1]),
                   (point[0], point[1] - 1),
                   (point[0], point[1] + 1)]
    
    return [point for point in neighborhood if 0 < point[0] < BOARD_SIZE and 0 < point[1] < BOARD_SIZE]




#calculates the liberties (empty adjacent points) for a stone or group of stones on the board.
def cal_liberty(points, board):
   
    liberties = [point for point in neighbors(points)
                 if not board.stonedict.get_groups('BLACK', point) and not board.stonedict.get_groups('WHITE', point)]
    
    return set(liberties)



#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



#Manage groups of points on a Go board for each color—black and white

class PointDict:
    def __init__(self):
        self.d = {'BLACK': {}, 'WHITE': {}}

    def get_groups(self, color, point):
        if point not in self.d[color]:
            self.d[color][point] = []
        return self.d[color][point]

    def set_groups(self, color, point, groups):
        self.d[color][point] = groups

    def remove_point(self, color, point):
        if point in self.d[color]:
            del self.d[color][point]

    def get_items(self, color):
        return self.d[color].items()
    

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class stonesGroup(object):

    #Initialize a new group of stones
    def __init__(self, point, stone_color, liberties):
        #stone's color
        self.color = stone_color 
        #stone's position
        if isinstance(point, list): self.points = point
        else:  self.points = [point]
        #stone's liberties
        self.liberties = liberties



    @property
    #How many liberties are in the group?
    def num_liberty(self):

        return len(self.liberties)


    #add only stones
    def add_stones(self, pointlist):
        
        self.points.extend(pointlist)
    


    #remove only liberties
    def remove_liberty(self, point):

        self.liberties.remove(point)


    #Summarize color, stones, liberties.
    def __str__(self):

        return '%s - stones: [%s]; liberties: [%s]' % \
               (self.color,
                ', '.join([str(point) for point in self.points]),
                ', '.join([str(point) for point in self.liberties]))
    

    
    def __repr__(self):
        return str(self)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# The game board and maintains the state of the game. 
class Board(object):

    #Initialize the board
    def __init__(self, next_color='BLACK'):


        self.winner = None  #there is no winner yet in the game.
        self.next_color = next_color  #which color is next to play
        self.legal_moves = []  #all the legal moves that a player can make from the current state of the board.
        self.end_by_no_legal_moves = False    #the game has not ended due to a lack of legal actions for the current player.
        self.counter_move = 0   # keep track of the number of moves that have been made in the game so far.


       
        # {color: {point: {groups}}}
        # map each point on the board to the groups, that it provides liberties to
        self.libertydict = PointDict() 

        #maps each point on the board to the stone (if any) that occupies that point.
        self.stonedict = PointDict()

    
    #dictionary groups with keys 'BLACK' and 'WHITE'. 
    #These lists will hold the groups of stones for each color on the board.
        self.groups = {'BLACK': [], 'WHITE': []}

    #keep track of groups with only one liberty left. 
    # Such groups are at risk of being captured on the opponent's next turn.
        self.endangered_groups = []  

    #store groups that have been captured and removed from the board.
        self.removed_groups = []  # This is assigned when game ends



    #Create a new group       
    def create_group(self, point, color):
        
        #calculates the liberties of the new stone placed at point
        lbt = cal_liberty(point, self)

        #creates a new instance of stonesGroup, representing a group of stones on the board with the given point, color, and calculated liberties.
        group = stonesGroup(point, color, lbt)
        self.groups[color].append(group)

        # Update endangered group
        #If the group has 1 or fewer liberties, it is considered endangered
        if len(group.liberties) <= 1:
            self.endangered_groups.append(group)

        # Update stonedict
        # tracks which groups occupy which points on the board.
        self.stonedict.get_groups(color, point).append(group)

        # Update libertydict
        #tracks the liberties of each group.
        for liberty in group.liberties:
            self.libertydict.get_groups(color, liberty).append(group)

        return group
      


    #removes a group from the board
    def remove_group(self, group):
     
        color = group.color

        # Update group list
        self.groups[color].remove(group)

        # Update endangered_groups
        if group in self.endangered_groups:
            self.endangered_groups.remove(group)

        # Update stonedict
        #It iterates over each point in the group, removing the group from the stonedict for that point. 
        # This signifies that the stones at these points are no longer part of any group.
        for point in group.points:
            self.stonedict.get_groups(color, point).remove(group)

        # Update libertydict
        for liberty in group.liberties:
            self.libertydict.get_groups(color, liberty).remove(group)




    #merges multiple groups into a single group when a new stone connects them
    def merge_groups(self, grouplist, point):
          

        color = grouplist[0].color  #all the groups start with the same color
        newgroup = grouplist[0] #initializes newgroup as the first group in the list  
        all_liberties = grouplist[0].liberties #liberties of this group

        # Add last move (update newgroup and stonedict)
        newgroup.add_stones([point])

        self.stonedict.get_groups(color, point).append(newgroup)

        #calculates the new liberties for the merged group by combining the liberties of all the groups in grouplist.
        all_liberties = all_liberties | cal_liberty(point, self)


        # Merge with other groups (update newgroup and stonedict)
        for group in grouplist[1:]:

            newgroup.add_stones(group.points)

            for p in group.points:

                self.stonedict.get_groups(color, p).append(newgroup)

            all_liberties = all_liberties | group.liberties

            self.remove_group(group)


        # Update newgroup liberties (point is already removed from group liberty)
        newgroup.liberties = all_liberties

        # Update libertydict
        for point in all_liberties:
            belonging_groups = self.libertydict.get_groups(color, point)
            if newgroup not in belonging_groups:
                belonging_groups.append(newgroup)

        return newgroup
    



    #returns a copy of the legal_moves list, ensuring that any changes made outside the class do not affect the internal state of the board object.
    def get_external_legal_moves(self):
        return self.legal_moves.copy()



    #don't call this function directly, use get_external_legal_moves
    def get_internal_legal_moves(self):
       
       #If there is already a winner, no further actions are legal, so it returns an empty list.
        if self.winner:
            return []

        #initializes two sets to keep track of the liberties adjacent
        endangered_lbt_current = set()   #the current player's groups
        endangered_lbt_opponent = set()  #the opponent's groups

        #If the opponent has any endangered groups (groups with one liberty), those points become the legal moves to target for a win.
        for group in self.endangered_groups:

            if group.color == self.next_color: 
                endangered_lbt_current = endangered_lbt_current | group.liberties

            else: 
                endangered_lbt_opponent = endangered_lbt_opponent | group.liberties


        #If the opponent has any endangered groups (groups with one liberty), those points become the legal actions to target for a win.
        # If there are opponent's endangered points, return these points to win
        if len(endangered_lbt_opponent) > 0:
            return list(endangered_lbt_opponent)


        #If the current player has endangered groups, the method prioritizes saving those groups.
        legal_moves = []

        if len(endangered_lbt_current) > 0:
            # If there are more than one self endangered points, return these points (losing the game)
            if len(endangered_lbt_current) > 1:

                legal_moves = list(endangered_lbt_current)

            # Rescue the sole endangered liberty if existing
            if len(endangered_lbt_current) == 1:

                legal_moves = list(endangered_lbt_current)
        else:

            legal_moves = set()

            for group in self.groups[opponent_color(self.next)]:

                #it effectively adds all the points from group.liberties to legal_moves, but only the unique ones that aren't already in legal_moves. 
                legal_moves = legal_moves | group.liberties 

            legal_moves = list(legal_moves)


        # filters out any suicidal moves, ensuring each action either has liberties after the move or connects to a friendly group with more than one liberty.
        legal_moves_filtered = []

        for move in legal_moves:

            if len(cal_liberty(move, self)) > 0:

                legal_moves_filtered.append(move)

            else:

                connected_self_groups = [self.stonedict.get_groups(self.next, p)[0] for p in neighbors(move)
                                         if self.stonedict.get_groups(self.next, p)]
                
                for self_group in connected_self_groups:

                    if len(self_group.liberties) > 1:

                        legal_moves_filtered.append(move)
                        break

        return legal_moves_filtered
    


    #removes a liberty from a group due to a stone being placed on the board
    def _shorten_liberty(self, group, point, color):

        group.remove_liberty(point) #removes the specified point from the group's liberties.

        if group.color != color:  # If opponent's group, check if winning or endangered groups

            if len(group.liberties) == 0:  # The new stone is opponent's, check if winning
                
                #If the group belongs to the opponent and loses all its liberties, it gets added to removed_groups, and the current player wins.
                self.removed_groups.append(group)  # Set removed_group
                self.winner = opponent_color(group.color)

            elif len(group.liberties) == 1:
                #If the group is reduced to one liberty, it's added to endangered_groups.
                self.endangered_groups.append(group)



    #updates the liberties of all groups affected by a stone being placed at point
    def shorten_liberty_for_groups(self, point, color):
  
        #first checks the liberties for the opponent's groups.
        # If placing a stone captures any opponent's groups, it updates the libertydict and potentially sets a winner.

        opponent = opponent_color(color)

        for group in self.libertydict.get_groups(opponent, point):

            self._shorten_liberty(group, point, color)

        self.libertydict.remove_point(opponent, point)  # update libertydict

    #If no opponent's groups are captured, it then checks the liberties for the current player's groups and updates the libertydict accordingly.        
        if not self.winner:

            for group in self.libertydict.get_groups(color, point):

                self._shorten_liberty(group, point, color)

        self.libertydict.remove_point(color, point)  # update libertydict
    




    # places a stone on the board at the specified point
    def put_stone(self, point, check_legal=False):

        if check_legal:

            #ilegal moves
            if point not in self.legal_moves:
                print('Error: illegal move, try again.')
                return False
            
        # If more than 400 moves (which shouldn't happen), print the board for debug
        if self.counter_move > 400:
            print(self)
            raise RuntimeError('More than 400 moves in one game! Board is printed.')

        # Get all self-groups containing this liberty
        self_belonging_groups = self.libertydict.get_groups(self.next, point).copy()

        # Remove the liberty from all belonging groups (with consequences updated such as winner)
        #removes the played point from the liberties of the adjacent groups and checks for any captures as a result of the move.
        self.shorten_liberty_for_groups(point, self.next)
        self.counter_move += 1

        if self.winner:

            self.next = opponent_color(self.next)
            return True


        # Update groups with the new point
        if len(self_belonging_groups) == 0:  # Create a group for the new stone
            new_group = self.create_group(point, self.next)

        else:  # Merge all self-groups in touch with the new stone
            new_group = self.merge_groups(self_belonging_groups, point)



        # Update whether is endangered group
        # endangered groups for opponent are already updated in shorten_liberty_for_groups
        if new_group in self.endangered_groups and len(new_group.liberties) > 1:
            self.endangered_groups.remove(new_group)
        elif new_group not in self.endangered_groups and len(new_group.liberties) == 1:
            self.endangered_groups.append(new_group)

        self.next = opponent_color(self.next)

        # Update legal_moves; if there are no legal actions for opponent, claim winning
        self.legal_moves = self._get_legal_moves()
        if not self.legal_moves:
            self.winner = opponent_color(self.next)
            self.end_by_no_legal_moves = True

        return True
    


    #applies an action (a move) to the board and returns the resulting board state.
    #returns the new board state.
    def generate_successor_state(self, action, check_legal=False):

        board = self.copy()
        board.put_stone(action, check_legal=check_legal)

        return board
    

        
    def __str__(self):

        str_groups = [str(group) for group in self.groups['BLACK']] + [str(group) for group in self.groups['WHITE']]

        return 'Next: %s\n%s' % (self.next, '\n'.join(str_groups))
    


    #It returns True if there are any groups in the stonedict for either black or white at the point, indicating the presence of a stone.
    def exist_stone(self, point):
        """To see if a stone has been placed on the board"""
        return len(self.stonedict.get_groups('BLACK', point)) > 0 or len(self.stonedict.get_groups('WHITE', point)) > 0


    #to simulate the game in a copy of the board
    def copy(self):

        board = Board(self.next)
        board.winner = self.winner

        group_mapping = {group: deepcopy(group) for group in self.groups['BLACK'] + self.groups['WHITE']}
        board.groups['BLACK'] = [group_mapping[group] for group in self.groups['BLACK']]
        board.groups['WHITE'] = [group_mapping[group] for group in self.groups['WHITE']]

        board.endangered_groups = [group_mapping[group] for group in self.endangered_groups]
        board.removed_groups = [group_mapping[group] for group in self.removed_groups]

        for point, groups in self.libertydict.get_items('BLACK'):
            if groups:
                board.libertydict.set_groups('BLACK', point, [group_mapping[group] for group in groups])
        for point, groups in self.libertydict.get_items('WHITE'):
            if groups:
                board.libertydict.set_groups('WHITE', point, [group_mapping[group] for group in groups])

        for point, groups in self.stonedict.get_items('BLACK'):
            if groups:
                board.stonedict.set_groups('BLACK', point, [group_mapping[group] for group in groups])
        for point, groups in self.stonedict.get_items('WHITE'):
            if groups:
                board.stonedict.set_groups('WHITE', point, [group_mapping[group] for group in groups])

        return board
    

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

