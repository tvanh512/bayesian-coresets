from ..base.iterative import GreedySingleUpdateCoreset
from ..base.errors import NumericalPrecisionError

import numpy as np
class FrankWolfeCoreset(GreedySingleUpdateCoreset):

  def __init__(self, tangent_space):
    super().__init__(N=tangent_space.num_vectors()) 
    self.T = tangent_space

  def _search(self):
    return (self.T[:].dot(self.T.residual(self.wts, self.idcs)) / self.T.norms()).argmax()

  def _step_coeffs(self, f):
    nsum = self.T.norms_sum()
    nf = self.T.norms()[f]
    xw = self.T.sum_w(self.wts, self.idcs)
    xs = self.T.sum()
    xf = self.T[f]

    gammanum = (nsum/nf*xf - xw).dot(xs-xw)
    gammadenom = ((nsum/nf*xf-xw)**2).sum()
    #print('gammanum : ' + str(gammanum) + ' gammadenom: ' + str(gammadenom) + ' step size: ' + str(gammanum/gammadenom))
    if gammanum < 0. or gammadenom == 0. or gammanum > gammadenom:
      raise NumericalPrecisionError
    return 1. - gammanum/gammadenom, nsum/nf*gammanum/gammadenom
  
  def _initialize(self):
    f = self._search()
    self._set(f, self.T.norms_sum()/self.T.norms()[f])

  def error(self):
    return self.T.error(self.wts, self.idcs)


