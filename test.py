
# tetris game and AI
from tetris import TetrisApp
from tetris_ai import TetrisAI

import unittest


test_boards = [

[[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[1,1,1,1,1,1,1,1,1,1]],

[[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,1,1,1,0],
[0,0,0,0,0,0,0,0,1,0],
[0,0,0,1,1,0,0,0,1,0],
[1,0,1,1,0,1,1,0,1,0],
[1,1,1,0,0,1,1,0,1,0],
[1,1,1,1,1,1,1,1,1,1]],

[[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,1,1,1,0],
[0,0,0,0,0,0,0,0,1,0],
[0,0,0,1,1,0,0,0,1,0],
[1,0,1,1,0,1,1,0,1,0],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1]],

[[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0],
[1,1,1,1,1,1,1,0,0,0],
[1,1,1,1,1,1,1,1,1,1]],

]

app = TetrisApp()
ai = TetrisAI(app)

# test indavidual function used for score moves
class TestEval(unittest.TestCase):

    def test_get_max_height(self):
      heights = []
      for board in test_boards:
        heights.append(ai.get_max_height(board))
      self.assertEqual(heights, [0,5,5,2]) 

    def test_get_roughness(self):
      roughs = []
      for board in test_boards:
        roughs.append(ai.get_roughness(board))
      self.assertEqual(roughs, [0,10,9,3]) 

    def test_get_hole_count(self):
      num_holes = []
      for board in test_boards:
        num_holes.append(ai.get_hole_count(board))
      self.assertEqual(num_holes, [0, 11,8,0])

    def test_get_rows_cleared(self):
      rows_cleared = []
      for board in test_boards:
        rows_cleared.append(ai.get_rows_cleared(board))
      self.assertEqual(rows_cleared, [0,0,1,0])

    def test_evel(self):
      ai.load_weights((-1,-1,-1,-1,-1,1))
      board_scores = ai.get_board_scores(test_boards)
 

class TestGenes(unittest.TestCase):
   
    def test_mix_genes(self):
      gene_1 = (1,2,3,4)
      gene_2 = (5,6,7,8)
      new_gene_1, new_gene_2 = ai.mix_genes(gene_1, gene_2)
      print(new_gene_1, new_gene_2)

    def test_mutate_gene(self):
      gene = (1.0,2.0,3.0,4.0)
      ai.mutation_val = 0.05
      new_gene = ai.mutate_gene(gene)
      print(new_gene)


if __name__ == '__main__':

    #app = TetrisApp()
    #ai = TetrisAI(app)
    
    unittest.main()

  
