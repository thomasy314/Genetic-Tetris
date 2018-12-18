

from collections import defaultdict, OrderedDict
import pygame, numpy, time, threading, random
import tetris

config = {
  'cell_size':  20,
  'cols':    10,
  'rows':    24,
  'delay':  750,
  'maxfps':  30
}

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
def join_matrixes(mat1, mat2, mat2_off, remove=False):
  off_x, off_y = mat2_off
  for cy, row in enumerate(mat2):
    for cx, val in enumerate(row):
      if val:
        set_val = val if not remove else 0
        try:
          mat1[cy+off_y-1  ][cx+off_x] = set_val
        except IndexError:
          print("out of bounds join")
  return mat1


# clearing a row for getting points
def remove_row(board, row):
  del board[row]
  return [[0 for i in range(config['cols'])]] + board

f = open("Data.txt", "w+")

'''
  TetriAI

  Fields:
    name - "Crehg"
    board --------- Current board layout
    cur_gen ------- Current generation number (starts at 1)
    cur_unit ------ Current gene being tested in the generation
    features ------ Features to base ai on
    feature_func -- Functions corresponding with each feature
    gen_weights --- Ordered dictionary of weight for the current generation
    height -------- Height of the pygame window
    mutation_val -- The range for which a gene's trait can be mutated if pick for mutation
    next_stones --- A list of tetriminoes to tell the game which is next
    num_units ----- The number of genes to gave in each generation (initial generation has 10x this)
    score --------- Current game score
    stone --------- The current stone
    stone_x ------- Current stone x position
    stone_y ------- Current stone y position
    tetris_app ---- The tetris game the ai interacts with
    weights ------- Weight gene for ai to make decisions with
    width --------- Width of the pygame window

'''
class TetrisAI(object):
  
  def __init__(self, tetris_app=None):
    self.name = "Crehg"
    self.tetris_app = tetris_app

    pygame.init()
    self.width = config['cell_size']*config['cols']
    self.height = config['cell_size']*config['rows']
    self.screen = pygame.display.set_mode((self.width, self.height ))

    ''' set fetures wanted here '''
    self.features = tuple()
    self.all_features = ("max_height", "cumulative_height", "relative_height", "roughness", "hole_count", "rows_cleared")

    self.feature_func = {"max_height" : self.get_max_height, 
                         "cumulative_height" : self.get_cumulative_height, 
                         "relative_height" : self.get_relative_height, 
                         "roughness" : self.get_roughness, 
                         "hole_count" : self.get_hole_count, 
                         "rows_cleared" : self.get_rows_cleared}
  '''
    ------------------------------------
              Pygame Display
    ------------------------------------
  '''


  def draw_matrix(self, matrix, offset, color=(255,255,255)):

    off_x, off_y  = offset
    for y, row in enumerate(matrix):
      for x, val in enumerate(row):
        if val:
          if color == (255, 255, 255):
            color = tetris.colors[val]
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
    self.show_score(str(self.score))

  # Show given message at the center of the board (for losing)
  def show_score(self, msg):
    for i, line in enumerate(msg.splitlines()):
      msg_image =  pygame.font.Font(
        pygame.font.get_default_font(), 12).render(
          line, False, (255,255,255), (0,0,0))
    
      msgim_center_x, msgim_center_y = msg_image.get_size()
      msgim_center_x //= 2
      msgim_center_y //= 2
    
      self.screen.blit(msg_image, (
        (self.width/10),
        (self.height)/10))

  '''
    ------------------------------------
            Getters and setters
    ------------------------------------
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
    ------------------------------------
                  Gameplay
    ------------------------------------
  '''

  '''
    self_train: 
      1. tests all moves that could be made
      2. makes the best move for the current gene
      3. gets the next tetromino (stone)
      4. check for end
      5. draws board (optional)

    parameters:
      display - Should it display the game running
      max_moves - Maximum number of moves for a gene until it moves on.
      training_rounds - Number of times a single gene is used. The more time the more accurate the score is
  '''

  def self_train(self, training_rounds=2, max_moves=500, display=True):

    moves_taken = 0
    cur_round = 1
    round_scores = []
 
    while True: 

      # test all possible moves
      possible_moves = self.get_possible_moves()
      move_scores = self.get_move_scores(possible_moves)

      # make best move
      self.make_move(move_scores, possible_moves)
      moves_taken += 1
  
      # get the next stone
      self.stone = self.get_next_stone()
      self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)

      # gameover or taken max number of moves
      if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)) or moves_taken == max_moves:

        round_scores.append(self.score)
        print("round ", cur_round, " finished of ", training_rounds, "|| Average Score: ", sum(round_scores)/len(round_scores))
        if cur_round == training_rounds:
          cur_round = 0 
          self.load_next_unit( sum(round_scores)/len(round_scores) )
          round_scores.clear()
          mean_score = 0

        moves_taken = 0
        cur_round += 1
        self.init_game()

      # draw display
      if display:
        self.screen.fill((0,0,0))
        self.draw_matrix(self.board, (0,0))
        self.draw_matrix(self.stone, (self.stone_x, self.stone_y), (0, 255, 0))
        pygame.display.update()
  

  def get_next_stone(self):
    if not hasattr(self, "next_stones") or len(self.next_stones) <= 0:
      #print("new")
      self.next_stones = numpy.random.permutation( len(tetris.tetris_shapes) )
    next_stone, self.next_stones = self.next_stones[-1], self.next_stones[:-1]

    return tetris.tetris_shapes[next_stone]

    
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
    if not check_collision(board,
                       stone,
                       (stone_x, stone_y)):
      stone_y = self.drop(board, stone, stone_x, stone_y)
    return stone_y

  '''
    Makes every possible move
    Returns a list of boards resulting from each move
  '''

  def get_possible_moves(self):
    if not (hasattr(self, "board") and hasattr(self, "stone")):
      raise ValueError("either board or stone do not exist for TetrisAI")

    moves = []
    
    for rotation in range(4):
    
      for i in range(len(self.board[0])):

        new_x = self.move(i, self.board, self.stone, self.stone_x, self.stone_y)
        new_y = self.drop(self.board, self.stone, new_x, self.stone_y) 
        join_matrixes(self.board, self.stone, (new_x, new_y))

        new_move = {"x":new_x, "y":new_y, "stone":numpy.copy(self.stone)}
        moves.append(new_move)

        join_matrixes(self.board, self.stone, (new_x, new_y), remove=True)

      self.stone = self.rotate_stone(self.board, self.stone, self.stone_x, self.stone_y)

    return moves

  # gets a list of scores from a list of board  

  def get_move_scores(self, moves):
    scores = []

    for mov in moves:
      
      join_matrixes(self.board, mov["stone"], (mov["x"], mov["y"]))

      new_score = self.eval_board(self.board)

      join_matrixes(self.board, mov["stone"], (mov["x"], mov["y"]), remove=True)
      scores.append( new_score )

    return scores 

  # takes possible moves and their scores and makes the best move

  def make_move(self, move_scores, possible_moves):
    
    best_index = move_scores.index( max(move_scores) )      
    best_move = possible_moves[best_index]

    join_matrixes( self.board, best_move["stone"], (best_move["x"], best_move["y"]))


    for i, row in enumerate(self.board):
      if 0 not in row:
        self.score += 10
        self.board = remove_row ( self.board, i)

    '''while True:
      for i, row in enumerate(self.board[:-1]):
        if 0 not in row:
          self.score += 10
          self.board = remove_row(
            self.board, i)
          break
      else:
        break'''

  # given scores what move should be made

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

  '''
    determines how good a move is based on weight genes
  '''

  def eval_board(self, board):

    if not (hasattr(self, "weights")):
      raise ValueError("TetrisAI has no weights")

    score = []

    for feat in self.features:
      score.append( self.feature_func[feat](board) * self.weights[feat] )

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
    Gets the number of spaces which are un reacable
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
      elif all(v == 0 for v in row):
        break
     
    return rows_cleared 


  '''
    genetic algorithm code
  '''


  '''
  Creates a gene with random weights
  if seeded it creates the weights based off the seeded gene
  '''
  def random_weights(self, seed=False, seed_range=0.1):
   
    weights = ()

    
    if seed:
      for val in seed:
        weights = weights + (random.uniform(-seed_range, seed_range) + val,)
    else:
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
  def start(self, num_units, seed, mutation_val=0.05, init_pop_const=10):

    self.num_units = num_units
    self.gen_weights = OrderedDict()
    self.cur_gen = 1
    self.cur_unit = -1
    self.mutation_val = mutation_val

    # get features from input
    for feature, val in seed.items():
      if feature in self.all_features:
        self.features = self.features + (feature,)
      else:
        raise ValueError(featuure + " is not a built in feature.\nPossible features: ")
        

    # test if we need to generate the feature weights
    gene = tuple(seed.values())

    if gene[0] != -999:

      self.gen_weights[ gene ] = 0
      for i in range(num_units * init_pop_const - 1):
        self.gen_weights[ self.random_weights(seed=gene) ] = 0

    else:

      # creating random initial population
      for i in range(num_units * init_pop_const):
        self.gen_weights[ self.random_weights() ] = 0
  

    self.load_next_unit(0)
    self.init_game()
    self.self_train()

  '''
    Starts a new game
      - new board
      - new stone
  '''  
  def init_game(self):
    self.score = 0
    self.board = [ [ 0 for w in range(config["cols"]) ] for h in range(config["rows"]-1) ]
    self.board.append( [1 for w in range(config["cols"])] )
    self.stone = self.get_next_stone()
    self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
    self.stone_y = 0

    return

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


