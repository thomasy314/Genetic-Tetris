
# tetris game and AI
#from tetris import TetrisApp
from tetris_trainer import TetrisApp
from tetris_ai_fast import TetrisAI
from multiprocessing import Process

import time, threading

def tetris_p():
    app = TetrisApp()
    ai = TetrisAI(app)

    threading.Thread(target=app.run).start()


if __name__ == '__main__':

  '''

  uncomment to run multiple trainings at one time

  processes = []
  num_tetris_ai = 5

  for m in range(num_tetris_ai):
    p = Process(target=tetris_p)
    p.start()
    processes.append(p)

  for p in processes:
    p.join()'''
      #self.features = ("max_height", "cumulative_height", "relative_height", "roughness", "hole_count", "rows_cleared")
  
  #app = TetrisApp()
  ai = TetrisAI()

  #threading.Thread(target=app.run).start()

  #ai.start(50, seed=(0.47132212759108, -0.8961845596357754, -0.3150062033525829, -0.281357362057707, -0.5260662419305762, 0.42665026288273705))

  ai.start(50, seed={"cumulative_height":-0.8961845596357754,
                     "roughness":-0.281357362057707, 
                     "hole_count":-0.5260662419305762, 
                     "rows_cleared":0.42665026288273705})

  #ai.start(100)



