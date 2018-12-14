

from collections import defaultdict, OrderedDict
import pygame, numpy, time, threading, random

# Rotates a shape clockwise
def rotate_clockwise(shape):
  return [ [ shape[y][x]
      for y in range(len(shape)) ]
    for x in range(len(shape[0]) - 1, -1, -1) ]

# checks if there is a collision in any direction
def check_collision(board, shape, offset):
  off_x, off_y = offset
  for cy, row in enumerate(shape):
    for cx, cell in enumerate(row):
      try:
        if cell and board[ cy + off_y ][ cx + off_x ]:
          return True
      except IndexError:
        return True
  return False

# Used for adding a stone to the board
def join_matrixes(mat1, mat2, mat2_off):
  off_x, off_y = mat2_off
  for cy, row in enumerate(mat2):
    for cx, val in enumerate(row):
      try:
        mat1[cy+off_y-1  ][cx+off_x] += val
      except IndexError:
        print("out of bounds join")
  return mat1

f = open("Data.txt", "w+")

'''
  TetriAI
'''
class TetrisAI(object):
  
  def __init__(self, tetris_app):
    self.name = "Crehg"
    self.tetris_app = tetris_app

    self.screen = pygame.display.set_mode((200, 480 ))

    ''' set fetures wanted here MAKE SURE TO CHANGE FUNCTIONS FOR EVALUATION BELOW'''
    #self.features = ("max_height", "cumulative_height", "relative_height", "roughness", "hole_count", "rows_cleared")
    self.features = ("cumulative_height", "roughness", "hole_count", "rows_cleared")

  def draw_matrix(self, matrix, offset, color=(255,255,255)):
    off_x, off_y  = offset
    for y, row in enumerate(matrix):
      for x, val in enumerate(row):
        if val:
          pygame.draw.rect(
            self.screen,
            color,
            pygame.Rect(
              (off_x+x) *
                20,
              (off_y+y) *
                20, 
              20,
              20),0)

  '''
    Getters and setters
  '''

  def set_weights(self, weight_dict):
    self.weights = defaultdict(int, weight_dict)

  def set_board(self, board):
    self.board = board

  def get_board(self):
    if not hasattr(self, "board"):
      raise ValueError("TerisAI does not have a board")

    return self.board

  def set_stone(self, stone, stone_x, stone_y):
    self.stone = stone
    self.stone_x = stone_x
    self.stone_y = stone_y

  def get_stone(self):
    if not hasattr(self, "stone"):
      raise ValueError("TertisAI does not have a stone")

    return (self.stone, self.stone_x, self.stone_y)

  '''
    Keyboard/Action controller
  '''

  def make_move(self, training=True):
    
    while True:
      cur_state = self.tetris_app.get_state()

      self.set_board(cur_state["board"])
      self.set_stone(cur_state["stone"], cur_state["stone_x"], cur_state["stone_y"])
  
      if not cur_state["needs_actions"]:
        continue

      actions = []

      if cur_state["gameover"] and training:
        self.load_next_unit( cur_state["score"] )
        actions.append("space")

 
  
      possible_boards = self.get_possible_boards()
      board_scores = self.get_board_scores(possible_boards)
      actions.extend(self.get_actions_from_scores(board_scores))
  
      self.tetris_app.add_actions(actions)


    #self.make_move()
    
  '''
    Actual AI stuff
  '''

  # move a piece horizontally
  def move(self, desired_x, board, stone, stone_x, stone_y):

    while(stone_x != desired_x):
      dist = desired_x - stone_x
      delta_x = int(dist/abs(dist))

      new_x = stone_x + delta_x
      if not check_collision(board,
                             stone,
                             (new_x, stone_y)):
        stone_x = new_x
      else:
        break
    return stone_x
 
  '''
    Rotate stone if no collision
  ''' 
  def rotate_stone(self, board, stone, stone_x, stone_y):

    new_stone = rotate_clockwise(stone)
    if not check_collision(board,
                           new_stone,
                           (stone_x, stone_y)):
      return new_stone
    return stone

  '''
    (Modified)
    Try moving piece down
      - if collision:
        1. add stone to board
        2. Check for row completion
        3. if no collision drop again
  ''' 
  def drop(self, board, stone, stone_x, stone_y):

    stone_y += 1
    if check_collision(board,
                       stone,
                       (stone_x, stone_y)):
      board = join_matrixes(
        board,
        stone,
        (stone_x, stone_y))
    else:
      self.drop(board, stone, stone_x, stone_y)
    return board, stone_y

  def get_possible_boards(self):
    if not (hasattr(self, "board") and hasattr(self, "stone")):
      raise ValueError("either board or stone do not exist for TetrisAI")
    
    cur_state = self.tetris_app.get_state()

    self.set_board(cur_state["board"])
    self.set_stone(cur_state["stone"], cur_state["stone_x"], cur_state["stone_y"])

    temp_board = numpy.copy(self.board)
    temp_stone = numpy.copy(self.stone)

    temper = numpy.copy(temp_stone)

    temp_x = self.stone_x
    temp_y = self.stone_y

    # contains all the board orientations possible with the current stone
    boards = []

    for j in range(4):


      for i in range(len(self.board[0])):

        temp_x = self.move(i, temp_board, temp_stone, temp_x, temp_y)
        temp_board, temp_y = self.drop(temp_board, temp_stone, temp_x, temp_y)


        boards.append(temp_board)

        temp_board = numpy.copy(self.board)
        temp_x = self.stone_x
        temp_y = self.stone_y

      temp_stone = self.rotate_stone(temp_board, temp_stone, temp_x, temp_y)


    
    '''self.stone = temp_stone
    self.board = temp_board
    self.stone_x = temp_x
    self.stone_y = temp_y'''

    return boards

  def get_board_scores(self, boards):
    scores = []

    for board in boards:
      new_score = self.eval_board(board)
      scores.append( new_score )

    return scores 

  def get_actions_from_scores(self, scores):
    actions = []

    # CHANGE THIS LATER
    best_score = scores.index( max(scores) )

    # rotate to proper orientation
    rotations = [ "up" for i in range( best_score//len(self.board[0]) )]
    actions.extend(rotations)

    # move to proper x pos
    desired_x = best_score % len(self.board[0]) 
    wanted_move = ""  
    if( desired_x > self.stone_x ):
      wanted_move = "right" 
    elif(desired_x < self.stone_x):
      wanted_move = "left"
    
    moves = [ wanted_move for i in range( abs(desired_x - self.stone_x) ) ]
    actions.extend(moves)

    # move to proper y pos
    levels =  self.get_column_heights(self.board)
    desired_y = levels[desired_x] + len(self.stone) 

    world_y = len(self.board) - self.stone_y
    num_drops = world_y - desired_y
    drops = [ "down" for i in range( num_drops ) ]
    #actions.extend(drops)

    return actions

  def eval_board(self, board):

    if not (hasattr(self, "weights")):
      raise ValueError("TetrisAI has no weights")


    ''' Make sure these function reflect the features you are using above '''
    score = []
    #score.append( self.get_max_height(board) * self.weights["max_height"])
    score.append( self.get_cumulative_height(board) * self.weights["cumulative_height"])
    #score.append( self.get_relative_height(board) * self.weights["relative_height"])
    score.append( self.get_roughness(board) * self.weights["roughness"])
    score.append( self.get_hole_count(board) * self.weights["hole_count"])
    score.append( self.get_rows_cleared(board) * self.weights["rows_cleared"])

    return sum(score)

  '''
    Gets the height of each column
  '''
  def get_column_heights(self, board):
    # get the hights of each column
    heghts = [0 for i in board[0]] 

    for y, row in enumerate(board[::-1]):
      for x, val in enumerate(row):
        if val != 0:
          heghts[x] = y
    
    return heghts

  '''
    Find max height in board
  '''
  def get_max_height(self, board):
    return max(self.get_column_heights(board))

  '''
    Gets the sum of all the columns
  '''
  def get_cumulative_height(self, board):
    return sum(self.get_column_heights(board))

  '''
    Gets the difference betweent he shortest and tallest height
  '''
  def get_relative_height(self, board):
    column_heights= self.get_column_heights(board)
    max_height = max(column_heights)
    min_height = min(column_heights)
    return max_height - min_height

  '''
    Get roughness
      determined by summing the hight
      absolute difference between a row at i and i+1
  '''
  def get_roughness(self, board):

    levels = self.get_column_heights(board)

    # get roughness
    roughness = 0

    for x in range(len(levels)-1):
      roughness += abs(levels[x] - levels[x+1]) 

    return roughness

  '''
    Get's the number of spaces which are un reacable
      A space is un reachable if there is another piece above it
      even if you could slip the piece in from the side
  '''
  def get_hole_count(self, board):
    levels = self.get_column_heights(board) 

    holes = 0

    for y, row in enumerate(board[::-1]):
      for x, val in enumerate(row):
        # if below max column height and is a zero
        if y < levels[x] and val==0:
          holes += 1 

    return holes

  '''
    Check how many rows will be cleared in this config
  '''
  def get_rows_cleared(self, board):
    # starts at -1 to account for bottom row which
    # is always all 1
    rows_cleared = -1
    
    for row in board:
      if 0 not in row:
        rows_cleared += 1
     
    return rows_cleared 


  '''
    genetic algorithm code
  '''


  '''
  Creates a gene with random weights
  if seeded it creates the weights based off the seeded gene
  '''
  def random_weights(self, seeded=False):
   
    weights = ()

    if seeded != False:
      for val in seeded:
        weights = weights + (random.uniform(-0.1, 0.1) + val,)
      return weights

    for f in self.features:
      weights = weights + (random.uniform(-1, 1),)
 
    return weights

  def load_weights(self, weight_tuple):
    self.weights = dict()

    for fn, f in enumerate(self.features):
      self.weights[f] = weight_tuple[fn]
      

  '''
  Creates the initial population and starts running

  num_units = the number of genes per generation (the initial generation is 10 times this value)
  mutation_val = the range for which a gene can be mutated
  seed = If you want to test a specific gene
  '''
  def start(self, num_units, mutation_val=0.05, seed=False):

    if seed:
      if not (isinstance(seed, tuple) or len(seed) != len(self.features)):
        raise ValueError('Seed not properly formatted. Make sure it is a tuple and has {} elements').format(len(self.features))
      self.load_weights(seed)
      self.make_move(training=False) 
    else:
      self.num_units = num_units
      self.gen_weights = OrderedDict()
      self.cur_gen = 1
      self.cur_unit = -1
      self.mutation_val = mutation_val
  
      for i in range(num_units * 10):
        self.gen_weights[ self.random_weights() ] = 0
  
      self.load_next_unit(0)
  
      self.make_move()

  '''
  Saves data from previous geneartion, preforms selection, crossover, and mutation
  '''
  def new_generation(self):

    weight_values = sorted( enumerate(self.gen_weights.values()), key= lambda x:x[1], reverse=True)
    print("\n\n")
    gen_score = sum(x[1] for x in weight_values)/len(weight_values)
    f.write("Generation {} score: {}\n".format(self.cur_gen,gen_score))
    print("Generation Score: ", gen_score )
    print("New Generation") 
    print("\n\n")
    self.cur_gen += 1   

    gen_keys = list(self.gen_weights.keys())
    new_gen = []

    # selection
    selected_units = [ gen_keys[tup[0]] for tup in weight_values[:self.num_units//len(self.board[0])] ]
     
    # crossover
    for i in range( len(selected_units)-1 ):
      unit1 = selected_units[i]
      unit2 = selected_units[i+1]

      new_unit1, new_unit2 = self.mix_genes(unit1, unit2)

      new_gen.append( new_unit1 ) 
      new_gen.append( new_unit2 ) 
      
    self.gen_weights = OrderedDict()
    self.cur_unit = -1

    for new_unit in new_gen:
      self.gen_weights[ new_unit ] = 0

    # mutation
    while len(self.gen_weights) < self.num_units:
      self.gen_weights[ self.mutate_gene( random.choice(new_gen) ) ] = 0


  def mix_genes(self, gene1, gene2):
    if(len(gene1) != len(gene2)):
      raise ValueError('A very specific bad thing happened.') 


    num_features = len(self.features)
    new_genes_to_switch = numpy.random.choice( range(num_features), num_features//2, replace=False )  

    new_gene1 = ()
    new_gene2 = ()


    for i in range( len(gene1) ):
      if i in new_genes_to_switch:
        new_gene1 = new_gene1 + ( gene2[i], )
        new_gene2 = new_gene2 + ( gene1[i], )
      else:
        new_gene1 = new_gene1 + ( gene1[i], )
        new_gene2 = new_gene2 + ( gene2[i], )
       
    return (new_gene1, new_gene2) 

  def mutate_gene(self, gene):


    num_features = len(self.features)

    # try for mutation with 5% change of success
    if random.randint(0,100) > 5:
      return gene

    genes_to_mutate = numpy.random.choice( range(num_features), random.randint(0, num_features), replace=False )

    new_gene = ()

    for i in range(len(gene)):
      mut_val = 0 
      if i in genes_to_mutate:
        mut_val = random.uniform(-self.mutation_val, self.mutation_val)
      new_gene = new_gene + ( gene[i] + mut_val,)

    return new_gene

  # load a gene into the ai to be used for Tetris
  def load_next_unit(self, score):

    if self.cur_unit >= 0:
      cur_unit = list(self.gen_weights.keys())[self.cur_unit]
      self.gen_weights[cur_unit] = score
      print("score: ", score) 
      print("--------------------------------------------------")

    self.cur_unit += 1
    print("Gen: ", self.cur_gen,"|| Unit: ", self.cur_unit)
    if self.cur_unit >= len(self.gen_weights):
      self.new_generation()
    else:
      new_unit = list(self.gen_weights.keys())[self.cur_unit]
      print("       ", new_unit)
      self.load_weights(new_unit)


