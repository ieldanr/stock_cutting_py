from glpk_master_setup import *
from glpk_master_setup_relaxed import *
from glpk_sub_setup import *
from glpk_solver import *
from cut_pattern import *
from initial_patterns_factory import *

class OptimalCutting:
  def __init__(self, stocks, demands):
    self.stocks = stocks
    self.demands = demands
    self.patterns = InitialPatternsFactory.get(self.stocks, self.demands)

  def optimize_patterns(self, patterns, stocks, demands):
    setup = GlpkMasterSetup(patterns, stocks, demands)
    solver = GlpkSolver(setup)
    lp = solver.solve()
    duals = solver.duals
    print "duals:"
    print '; '.join('%g' % (d) for d in duals)
    lamdas = duals[0:len(self.demands)]
    deltas = duals[len(self.demands):len(duals)]
    return lp, solver.relaxed_value, deltas, lamdas

  def generate_pattern(self, stocks, deltas, demands, lamdas):
    setup = GlpkSubSetup(stocks, deltas, demands, lamdas)
    solver = GlpkSolver(setup)
    lp = solver.solve()
    print "sub problem value: %g" % lp.obj.value
    return self.get_pattern_from_lp(lp), lp.obj.value

  def iterate(self):
    lp, relaxed_value ,deltas, lamdas = self.optimize_patterns(self.patterns, self.stocks, self.demands)
    self.deltas = deltas
    self.lamdas = lamdas
    new_pattern, value_of_pattern = self.generate_pattern(self.stocks, self.deltas, self.demands, self.lamdas)
    self.patterns.append(new_pattern)
    return lp, value_of_pattern

  def get_pattern_from_lp(self, lp):
    solution = [c.primal for c in lp.cols]
    quantities = solution[0:len(self.demands)]
    stock_index = -1
    stock = None
    for index, sol in enumerate(solution[len(self.demands):len(solution)]):
      if sol == 1:
        stock = self.stocks[index]
        break
    return CutPattern(stock, self.demands, quantities)

  def solve(self):
    lp, rv = self.iterate()
    print "%g" % rv
    while(rv < -.0001):
      lp, rv = self.iterate()
      print "%g" % rv

    self.patterns.pop()
    return lp, self.patterns
