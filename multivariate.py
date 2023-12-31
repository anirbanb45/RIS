from __future__ import division
import numpy as np
import scipy.special as special
import itertools
def detBoundaries(params, tol):
  '''Determine rectangular boundaries of integration region of MeijerG function.'''
  boundary_range = np.arange(0, 50, 0.05)
  dims = len(params[0])
  boundaries = np.zeros(dims)
  for dim_l in range(dims):
    points = np.zeros((boundary_range.shape[0], dims))
    points[:, dim_l] = boundary_range
    abs_integrand = np.abs(compMultiMeijerGIntegrand(points, params))
    index = np.max(np.nonzero(abs_integrand>tol*abs_integrand[0]))
    boundaries[dim_l] = boundary_range[index]
  return boundaries
def compMultiMeijerGIntegrand(y, params):
  ''' Compute complex integrand of MeijerG function at points given by rows of matrix y.'''
  z, mn, pq, c, d, a, b = params
  m, n = zip(*mn)

  p, q = zip(*pq)
  npoints, dims = y.shape
  s = 1j*y
  lower = np.zeros(dims)
  upper = np.zeros(dims)
  for dim_l in range(dims):
    if b[dim_l]:
      bj= b[dim_l][0]

      bj = np.array(bj[:n[dim_l+1]])

      lower[dim_l] = -np.min(bj)
    else:
      lower[dim_l] = -100
    if a[dim_l]:
      aj = a[dim_l][0]
      aj = np.array(aj[:m[dim_l+1]])
      upper[dim_l] = np.min((1-aj))
    else:
      upper[dim_l] = 0
  mindist = np.linalg.norm(upper-lower)
  sigs = 0.5*(upper+lower)
  for j in range(m[0]):
    num = 1 - c[j][0] - np.sum(c[j][1:] * lower)
    print(num)
    cnorm = np.linalg.norm(d[j][1:])
    newdist = np.abs(num) / cnorm
    if newdist < mindist:
      mindist = newdist
      sigs = lower + 0.5*num*np.array(d[j][1:])/(cnorm*cnorm)
  s += -sigs
  s1= np.c_[np.ones((npoints, 1)), s]
  prod_gam_num = prod_gam_denom = 1+0j

  s2=s1[:,1:4]
  s2=np.sum(s2, axis = 1)

  for j in range(m[0]):

    prod_gam_num *= special.gamma(s2+c[j])

  for j in range(q[0]):
    prod_gam_denom *= special.gamma(s2+d[j])
  for j in range(m[0], p[0]):
    prod_gam_denom *= special.gamma(1-s2-c[j])

  for dim_l in range(dims):
    for j in range(m[dim_l+1]):

      prod_gam_num *= special.gamma(1 - a[dim_l][j][0] +s[:,dim_l])


    for j in range(n[dim_l+1]):

      prod_gam_num *= special.gamma(b[dim_l][0][j] -s[:,dim_l])

    for j in range(m[dim_l+1], p[dim_l+1]):


      prod_gam_denom *= special.gamma(a[dim_l][1][j-1] -s[:,dim_l])

    for j in range(n[dim_l+1], q[dim_l+1]):
      prod_gam_denom *= special.gamma(1 - b[dim_l][1][j-1] +s[:,dim_l])

  zs = np.power(z, s)


  result = (prod_gam_num/prod_gam_denom)*np.prod(zs, axis=1)/(2*np.pi)**dims
  return result
def compMultiMeijerG(params, nsubdivisions, boundaryTol=0.0001):
  '''Estimate multivariate integral using rectangular quadrature.
  Inputs: 'params’: list containing z, mn, pq, c, d, a, b. 'nsubdivisions’: the number of
  divisions taken along each dimension. 'boundaryTol’: tolerance used for determining
  the boundaries. Output: 'result’: the estimated value of the MeijerG function...'''
  boundaries = detBoundaries(params, boundaryTol)
  dim = boundaries.shape[0]
  signs = list(itertools.product([1,-1], repeat=dim))
  code = list(itertools.product(range(int(nsubdivisions/2)), repeat=dim))
  quad = 0
  res = np.zeros((0))
  for sign in signs:
    points = np.array(sign)*(np.array(code)+0.5)*boundaries*2/nsubdivisions
    res = np.r_[res,np.real(compMultiMeijerGIntegrand(points, params))]
    quad += np.sum(compMultiMeijerGIntegrand(points, params))
  volume = np.prod(2*boundaries/nsubdivisions)
  result = quad*volume
  return result

