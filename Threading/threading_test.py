def do_math_homework():

    res = 0
    for i in range(100_000_000):
        res += i
    return res

def do_physics_homework(num_of_tasks:int):
  """same as do_math_homework)"""
def do_chemistry_homework(num_of_tasks:int):
  """same as do_math_homework)"""

from multiprocessing import Process

processlist = []

processlist.append(Process(target=do_math_homework))
processlist.append(Process(target=do_physics_homework))
processlist.append(Process(target=do_chemistry_homework))

for t in processlist:
  t.start()

for t in processlist:
  t.join()