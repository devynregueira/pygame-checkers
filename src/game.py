import pygame

screen_width = 800
screen_height = 600
box_width = 100 #width of each tile
box_height = 75 #height of each tile
circle_rad = box_height/3 #radius of a piece
col_bounds = [x * box_width for x in range(9)]
row_bounds = [y * box_height for y in range(9)]

#colors for tiles and pieces
w = (255,255,255)
b = (0,0,0)
r = (255,0,0)
y = (255,255,0)

def is_even(num):
    return num % 2 == 0

#reference lists to easily pattern the board
odd_row = [b,w,b,w,b,w,b,w]
even_row = [w,b,w,b,w,b,w,b]

#basis for the board
matrix = [even_row if is_even(x) else odd_row for x in range(8)]

#simplify creating the "king" graphic
def offset_triangle(point_list,offset_by):
    new_list = [[x[0] + offset_by, x[1]] for x in point_list]
    return new_list

#add the "king" graphic to a piece which has become a king
def draw_crown(center,screen):
    p_one = (center[0], center[1] - circle_rad/2) #top middle
    p_two = (center[0] - circle_rad/4, center[1] + circle_rad/2) #bottom left
    p_three = (center[0] + circle_rad/4, center[1] + circle_rad/2) #bottom right
    
    middle_triangle = [p_one,p_two,p_three] #then offset X by 1/4 of the box in either direction
    left_triangle = offset_triangle(middle_triangle,(circle_rad/3 * -1))
    right_triangle = offset_triangle(middle_triangle,circle_rad/3)

    pygame.draw.polygon(screen,(120, 81, 169),left_triangle)
    pygame.draw.polygon(screen,(120, 81, 169),middle_triangle)
    pygame.draw.polygon(screen,(120, 81, 169),right_triangle)

#board is comprised of 64 tiles
class Tile:
    #initialize tile with critical attributes for drawing, associating with a click, and interacting with pieces
    def __init__(self, screen, row_ind, col_ind, color, center, piece):
        self.screen = screen
        self.col_ind = col_ind
        self.row_ind = row_ind
        self.color = color
        self.center = center
        self.base_rect = pygame.Rect(box_width * col_ind,box_height * row_ind,box_width, box_height)
        self.piece = piece 
    #draw the original tile or redraw it with the correct attributes after a piece is added or removed
    def draw_tile(self):
        pygame.draw.rect(self.screen, self.color, self.base_rect)
        #make sure to add the piece back to the tile once it's redrawn after being highlighted
        if self.piece:
            self.piece.redraw()
    #highlight the tile blue to indicate to player that its piece is designated to move
    def highlight_selected(self):
        if self.piece != False:
            new_rect = pygame.Rect(box_width * self.col_ind,box_height * self.row_ind,box_width, box_height)
            pygame.draw.rect(self.screen, (173, 216, 230), new_rect)
            self.piece.redraw()

#each player begins with 12 pieces, located on all the black squares within 3 rows of their boundary
class Piece:
    #initialize piece with critical attributes for drawing, associating with a click, and permissable movement
    def __init__(self, screen, color, center, player, is_king):
        self.is_king = is_king
        self.screen = screen
        self.color = color
        self.center = center
        self.player = player
    #quick method to re-render piece after it moves
    def redraw(self):
        self.draw_to_screen(self.is_king,self.center)
    #original render or rerender with location information and king boolean
    def draw_to_screen(self, is_king, center):
        self.center = center
        self.is_king = is_king
        pygame.draw.circle(self.screen,self.color,center,circle_rad)
        if is_king:
            draw_crown(center,screen)

#populate the list of pieces at the beginning of a game; a color entry indicates a piece, False indicates no piece
def fill_piece_matrix():
    piece_matrix = []
    for row_num,row in enumerate(matrix):
        output_row = []
        for col_num, col in enumerate(row):
            if row_num < 3: #player 1
                #piece placement logic
                to_append = False if is_even(row_num) and is_even(col_num) else y if is_even(col_num) else y if is_even(row_num) else False
                to_append = False if to_append == False else [to_append,1]
            elif row_num >= 5: #player 2
                #piece placement logic
                to_append = False if is_even(row_num) and is_even(col_num) else r if is_even(col_num) else r if is_even(row_num) else False
                to_append = False if to_append == False else [to_append,2]
            else: #un-assigned rows in the middle
                #no pieces to place
                to_append = False 
            #append either the color of the piece (y or r) to row, or False to indicate no piece
            output_row.append(to_append)
        #append the row to the matrix
        piece_matrix.append(output_row)
    #state["piece_matrix"] = piece_matrix
    return piece_matrix

#create the board and fill it with pieces, as layed out by the fill_piece_matrix function
def fill_board(piece_matrix):
    board = []
    for row_index, row in enumerate(matrix):
        piece_row = piece_matrix[row_index]
        board.append([])
        for col_index, color in enumerate(row):
            #locate the center of the tile at this index
            cntr = (box_width * col_index + (box_width/2), box_height * row_index + (box_height/2))
            #extract the entry at those coordinates: False if no piece, else color of the piece
            piece_box = piece_row[col_index]
            #if no piece at those coordinates
            if piece_box == False:
                #instantiate and draw a pieceless tile
                tile = Tile(screen, row_index, col_index, color, cntr, False)
                board[row_index].append(tile)
                tile.draw_tile()
                continue;
            #if there is a piece at those coordinates
            else: 
                #instantiate the piece with the indicated color
                new_piece = Piece(screen, color=piece_box[0], center=cntr, player=piece_box[1], is_king=False)
                #instantiate and draw the tile
                tile = Tile(screen, row_index, col_index, color, cntr, new_piece)
                board[row_index].append(tile)
                tile.draw_tile()
                #draw the piece on top of the new tile
                new_piece.draw_to_screen(False, cntr) #None
    #board is a 2D list containing tiles which can be easily referenced and altered as moves are made
    return board

#return the appropriate Tile instance based on the coordinates of a player's click
def snap_to_tile(mouse_position):
    col = mouse_position[0]
    row = mouse_position[1]
    col_index = [i for i in range(len(col_bounds)) if col_bounds[i] < col + box_width][-1] - 1 
    row_index = [i for i in range(len(row_bounds)) if row_bounds[i] < row + box_height][-1] - 1

    return board[row_index][col_index] #state["board"][row_index][col_index]

#determine whether turn may continue after the user already captured a piece
def is_continuable(player, row, col, vert, is_king):
    #calculate the permissable row coordinate of a hypothetical subsequent move
    vert_ind = row + vert * 2
    #determine whether the only possible row or column destination of a subsequent move is outside the board
    disqualify = vert_ind > 7 or vert_ind < 0 or (((player == 2 and row < 2) or (player == 1 and row > 5)) and is_king == False)

    #if so, return False to end player turn
    if disqualify:
        return False
    
    #determine whether there is an intervening piece in either horizontal direction to leap/capture
    left_target = "DQ" if col < 2 else board[row + vert * 2][col - 2].piece
    right_target = "DQ" if col > 5 else board[row + vert * 2][col + 2].piece

    #if not, end turn
    if left_target != False and right_target != False:
        return False

    #if there is an intervening piece to the left
    if left_target == False:
        #ensure player doesn't leap outside the board; identify the piece object if they won't
        left_tween = False if col < 2 else board[row + vert][col - 1].piece
        #if there is an intervening piece and a permissible space beyond
        if left_tween != False:
            #if it is player's opponent's piece
            if left_tween.player != player:
                #player may continue to move
                return True

    #same logic for movement to the right
    if right_target == False:
        right_tween = False if col > 5 else board[row + vert][col + 1].piece
        if right_tween != False:
            if right_tween.player != player:
                return True
            else:
                #player cannot continue
                return False

#draw and populate the board
def restartGame():
    global screen, piece_matrix, board, state
    #instantiate the pygame screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    #create 2D list indicating coordinates and color of pieces
    piece_matrix = fill_piece_matrix();
    #draw the tiles and pieces to the screen; create global "board" variable for interacting with tiles by coordinates
    board = fill_board(piece_matrix);
    # Set initial turn as window title
    pygame.display.set_caption("Player 1's Turn")
    #set global state, which will be used to govern and document moves
    state = {
        "player_turn": 1,
        "previous_tile": False, #to redraw after being highlighted
        "selected_tile": False, #tile with piece to be moved
        "destination_tile": False, #tile to move piece to
        "is_continuing": False, #to prevent user from selecting another tile to move
        "piece_count": [12,12] #count of each players pieces, 1 2
    }
    
#start new game
restartGame();
    
def moveManagement(tile_obj):
    piece_obj = tile_obj.piece #False if Tile isn't associated with a Piece, else Piece object
    plyr = state["player_turn"]
    
    #If the user has selected a tile with a piece on it (they're choosing which piece to move)
    if piece_obj != False: 
        #if user has selected one of their own pieces, and isn't limited to further capture moves (is_continuing)
        if piece_obj.player == plyr and state["is_continuing"] == False:
            state["previous_tile"] = state["selected_tile"]; #if they'd already selected a tile, it's now the old tile
            state["selected_tile"] = tile_obj.center #store the newly selected tile for future reference
            
            #if they had selected a tile previously from which to make a move
            if state["previous_tile"] != False: 
                prev = snap_to_tile(state["previous_tile"]) 
                prev.draw_tile() #unhighlight that tile
        
            tile_obj.highlight_selected() #highlight the selected tile

    #user is now choosing where they want the piece from the tile they selected to go (they're making a move)
    elif state["selected_tile"] != False: 
        
        is_valid_move = tile_obj.piece == False #prevent the move if their destination tile already has a piece on it

        if is_valid_move:
            
            old_piece_tile = snap_to_tile(state["selected_tile"]) #tile object containing the piece to move

            new_col = tile_obj.col_ind  #destination tile column
            old_col = old_piece_tile.col_ind  #origin tile column
            new_row = tile_obj.row_ind  #destination tile row
            old_row = old_piece_tile.row_ind  #origin tile row

            old_piece = old_piece_tile.piece  #the piece which the player is moving

            #logic to determine vertical movement options based on piece location and king-ship
            was_last_row = (plyr == 1 and old_row == 7) or (plyr == 2 and old_row == 0) 
            was_king = old_piece.is_king or was_last_row 
            is_king = was_king or (plyr == 1 and new_row == 7) or (plyr == 2 and new_row == 0)
            vert_increment = int((new_row - old_row)/2) if was_king else 1 if plyr == 1 else -1  #descending toward 7 for p1, p2 ascending toward 0

            is_innocent = abs(old_col - new_col) == 1 #if the hz increment is only 1/-1, no capture is attempted
            is_innocent = is_innocent and old_row + vert_increment == new_row or (is_king and abs(old_row - new_row) == 1)  #not a capture

            #if it wasn't a capture-move
            if is_innocent:

                #ensure they aren't in a continuing state (subsequent moves after an in-turn capture);
                is_valid_move = state["is_continuing"] == False #prevent non-capture moves for continuation moves

            #if it is a capture-move
            else:
                
                #determining permissable direction and degree of movement
                acceptable_vert = vert_increment * 2  
                acceptable_lat = 2
                lat_direction = -1 if old_col > new_col else 1 
                tween_tile = board[old_row + vert_increment][old_col + lat_direction]
                tween_piece = tween_tile.piece #piece being jumped

                #logic to determine permissability of the move
                is_valid_move = tween_piece != False #there's a piece being jumped
                is_valid_move = is_valid_move and tween_piece.player != plyr #it's the opponents piece
                #direction and degree are valid, based on player and whether the piece is a king
                is_valid_move = is_valid_move and (old_row + acceptable_vert == new_row or (is_king and abs(old_row - new_row) == 2))
                is_valid_move = is_valid_move and (old_col + (lat_direction * acceptable_lat) == new_col )

            if is_valid_move: 
                #remove the piece from the origin tile; redraw the tile without a piece
                moved_piece = old_piece_tile.piece
                old_piece_tile.piece = False
                old_piece_tile.draw_tile();

                #draw new piece on destination tile
                new_center = tile_obj.center
                state["destination_tile"] = new_center
                tile_obj.piece = moved_piece
                moved_piece.center = new_center
                moved_piece.draw_to_screen(is_king, new_center)     

                if is_innocent == False: 
                    #update the state to reflect the new number of pieces
                    count_index = tween_tile.piece.player - 1
                    piece_counts = state["piece_count"]
                    new_count = piece_counts[count_index] - 1
                    piece_counts[count_index] = new_count
                    state["piece_count"] = piece_counts

                    #remove captured piece from board
                    tween_tile.piece = False
                    tween_tile.draw_tile();
                    
                    #end the game and start a new game when one player is out of pieces
                    if(new_count == 0):
                        restartGame();
                        return True; 

                    #determine whether the player can make subsequent captures after the initial capture
                    continuable = is_continuable(plyr, new_row, new_col, vert_increment, is_king)
                    continuable = True if continuable else False if is_king == False else \
                        is_continuable(plyr, new_row, new_col, vert_increment * -1, is_king)

                    if continuable:
                        state["is_continuing"] = True;
                    else:
                        state["is_continuing"] = False;
                
                #if player is not currently continuing
                if state["is_continuing"] != True:
                    #reset state for next player's turn
                    state["player_turn"] = 1 if state["player_turn"] == 2 else 2
                    state["previous_tile"] = False #to redraw after being highlighted
                    state["selected_tile"] = False #tile with piece to be moved
                    state["destination_tile"] = False
                    state["is_continuing"] = False

                    pygame.display.set_caption("Player " + str(state["player_turn"]) + "'s Turn")
                
                #if player is continuing after a capture
                else: 
                    state["previous_tile"] = False;
                    state["selected_tile"] = tile_obj.center #new tile selected
                    tile_obj.highlight_selected();
                    moveManagement(tile_obj) #rerun function down limited "is_continuing" logic tree
