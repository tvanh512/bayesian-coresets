import numpy as np
import warnings
from .coreset import Coreset


class NumericalPrecisionError(Exception):
  pass

class IterativeCoreset(Coreset):
  def _build(self, M):
    Mnew = self.M
    for m in range(self.M, M):
      if self.reached_numeric_limit:
        break
      stepped = self._step()
      if type(stepped) is not bool:
        raise ValueError(self.alg_name+'._build(): _step() must return a bool denoting failure or success.')
      if stepped:
        Mnew = m+1
    return Mnew

  def _step(self):
    raise NotImplementedError()

class SingleGreedyCoreset(IterativeCoreset):

  def _step(self):
    #search for the next best point
    retried_already = False
    while True:
      try:
        f = self._search()
        if type(f) is not int or f < 0:
          raise ValueError(self.alg_name+'._step(): _search() must return a nonnegative integer.')
      except NumericalPrecisionError:
        if retried_already:
          warnings.warn(self.alg_name+'._step(): Greedy next point selection failed a second time. Assuming numeric limit reached.')
          self.reached_numeric_limit = True
          return False
        else:
          warnings.warn(self.alg_name+'._step(): Greedy next point selection failed. Retrying...')
          retried_already = True
          self._prepare_retry_search()

    #get step length
    retried_already = False
    while True:
      try:
        #alpha is the downweighting for all other data
        #beta is the new weight for single selected data
        ret = self._step_coeffs(f)
        if type(ret) is not tuple or len(ret) != 2:
          raise ValueError(self.alg_name+'._step(): _step_coeffs() must return a 2-tuple of floats.')
        alpha, beta = ret
      except NumericalPrecisionError:
        if retried_already:
          warnings.warn(self.alg_name+'._step(): Step coefficient computation failed a second time. Assuming numeric limit reached.')
          self.reached_numeric_limit = True
          return False
        else:
          warnings.warn(self.alg_name+'._step(): Step coefficient computation failed. Retrying...')
          retried_already = True
          self._prepare_retry_search()

    #update the weights
    self.wts *= alpha
    #it's possible wts[f] becomes negative if beta approx -wts[f], so threshold
    self.wts[f] = max(self.wts[f]+beta, 0)

    self._update_cache(alpha, beta)

  def _search(self):
    raise NotImplementedError()

  def _step_coeffs(self, f):
    raise NotImplementedError()

  def _prepare_retry_step(self):
    pass #implementation optional
  
  def _prepare_retry_search(self):
    pass #implementation optional

  def _update_cache(self):
    pass #implementation optional

  



