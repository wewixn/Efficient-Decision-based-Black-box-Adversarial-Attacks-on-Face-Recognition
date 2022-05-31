# -*- coding: utf-8 -*-
# """
# Created on Tue Jul 11 06:54:28 2017

# @author: zhaoyafei
# """

import numpy as np
from numpy.linalg import inv, norm, lstsq
from numpy.linalg import matrix_rank as rank


# """
# Introduction:
# ----------
# numpy implemetation form matlab function CP2TFORM(...)
# with 'transformtype':
#     1) 'nonreflective similarity'
#     2) 'similarity'


# MATLAB code:
# ----------
# %--------------------------------------
# % Function  findNonreflectiveSimilarity
# %
# function [trans, output] = findNonreflectiveSimilarity(uv,xy,options)
# %
# % For a nonreflective similarity:
# %
# % let sc = s*cos(theta)
# % let ss = s*sin(theta)
# %
# %                   [ sc -ss
# % [u v] = [x y 1] *   ss  sc
# %                     tx  ty]
# %
# % There are 4 unknowns: sc,ss,tx,ty.
# %
# % Another way to write this is:
# %
# % u = [x y 1 0] * [sc
# %                  ss
# %                  tx
# %                  ty]
# %
# % v = [y -x 0 1] * [sc
# %                   ss
# %                   tx
# %                   ty]
# %
# % With 2 or more correspondence points we can combine the u equations and
# % the v equations for one linear system to solve for sc,ss,tx,ty.
# %
# % [ u1  ] = [ x1  y1  1  0 ] * [sc]
# % [ u2  ]   [ x2  y2  1  0 ]   [ss]
# % [ ... ]   [ ...          ]   [tx]
# % [ un  ]   [ xn  yn  1  0 ]   [ty]
# % [ v1  ]   [ y1 -x1  0  1 ]
# % [ v2  ]   [ y2 -x2  0  1 ]
# % [ ... ]   [ ...          ]
# % [ vn  ]   [ yn -xn  0  1 ]
# %
# % Or rewriting the above matrix equation:
# % U = X * r, where r = [sc ss tx ty]'
# % so r = X\U.
# %

# K = options.K;
# M = size(xy,1);
# x = xy(:,1);
# y = xy(:,2);
# X = [x   y  ones(M,1)   zeros(M,1);
#      y  -x  zeros(M,1)  ones(M,1)  ];

# u = uv(:,1);
# v = uv(:,2);
# U = [u; v];

# % We know that X * r = U
# if rank(X) >= 2*K
#     r = X \ U;
# else
#     error(message('images:cp2tform:twoUniquePointsReq'))
# end

# sc = r(1);
# ss = r(2);
# tx = r(3);
# ty = r(4);

# Tinv = [sc -ss 0;
#         ss  sc 0;
#         tx  ty 1];

# T = inv(Tinv);
# T(:,3) = [0 0 1]';

# trans = maketform('affine', T);
# output = [];

# %-------------------------
# % Function  findSimilarity
# %
# function [trans, output] = findSimilarity(uv,xy,options)
# %
# % The similarities are a superset of the nonreflective similarities as they may
# % also include reflection.
# %
# % let sc = s*cos(theta)
# % let ss = s*sin(theta)
# %
# %                   [ sc -ss
# % [u v] = [x y 1] *   ss  sc
# %                     tx  ty]
# %
# %          OR
# %
# %                   [ sc  ss
# % [u v] = [x y 1] *   ss -sc
# %                     tx  ty]
# %
# % Algorithm:
# % 1) Solve for trans1, a nonreflective similarity.
# % 2) Reflect the xy data across the Y-axis,
# %    and solve for trans2r, also a nonreflective similarity.
# % 3) Transform trans2r to trans2, undoing the reflection done in step 2.
# % 4) Use TFORMFWD to transform uv using both trans1 and trans2,
# %    and compare the results, Returnsing the transformation corresponding
# %    to the smaller L2 norm.

# % Need to reset options.K to prepare for calls to findNonreflectiveSimilarity.
# % This is safe because we already checked that there are enough point pairs.
# options.K = 2;

# % Solve for trans1
# [trans1, output] = findNonreflectiveSimilarity(uv,xy,options);


# % Solve for trans2

# % manually reflect the xy data across the Y-axis
# xyR = xy;
# xyR(:,1) = -1*xyR(:,1);

# trans2r  = findNonreflectiveSimilarity(uv,xyR,options);

# % manually reflect the tform to undo the reflection done on xyR
# TreflectY = [-1  0  0;
#               0  1  0;
#               0  0  1];
# trans2 = maketform('affine', trans2r.tdata.T * TreflectY);


# % Figure out if trans1 or trans2 is better
# xy1 = tformfwd(trans1,uv);
# norm1 = norm(xy1-xy);

# xy2 = tformfwd(trans2,uv);
# norm2 = norm(xy2-xy);

# if norm1 <= norm2
#     trans = trans1;
# else
#     trans = trans2;
# end
# """

class MatlabCp2tormException(Exception):
    def __str__(self):
        return 'In File {}:{}'.format(
                __file__, super.__str__(self))

def tformfwd(trans, uv):
    # '''
    # Function:
    # ----------
    #     apply affine transform 'trans' to uv

    # Parameters:
    # ----------
    #     @trans: 3x3 np.array
    #         transform matrix
    #     @uv: Kx2 np.array
    #         each row is a pair of coordinates (x, y)

    # Returns:
    # ----------
    #     @xy: Kx2 np.array
    #         each row is a pair of transformed coordinates (x, y)
    # '''
    uv = np.hstack((
        uv, np.ones((uv.shape[0], 1))
    ))
    xy = np.dot(uv, trans)
    xy = xy[:, 0:-1]
    return xy


def tforminv(trans, uv):
    # '''
    # Function:
    # ----------
    #     apply the inverse of affine transform 'trans' to uv

    # Parameters:
    # ----------
    #     @trans: 3x3 np.array
    #         transform matrix
    #     @uv: Kx2 np.array
    #         each row is a pair of coordinates (x, y)

    # Returns:
    # ----------
    #     @xy: Kx2 np.array
    #         each row is a pair of inverse-transformed coordinates (x, y)
    # '''
    Tinv = inv(trans)
    xy = tformfwd(Tinv, uv)
    return xy


def findNonreflectiveSimilarity(uv, xy, options=None):
    # """
    # Function:
    # ----------
    #     Find Non-reflective Similarity Transform Matrix 'trans':
    #         u = uv[:, 0]
    #         v = uv[:, 1]
    #         x = xy[:, 0]
    #         y = xy[:, 1]
    #         [x, y, 1] = [u, v, 1] * trans

    # Parameters:
    # ----------
    #     @uv: Kx2 np.array
    #         source points each row is a pair of coordinates (x, y)
    #     @xy: Kx2 np.array
    #         each row is a pair of inverse-transformed
    #     @option: not used, keep it as None

    # Returns:
    #     @trans: 3x3 np.array
    #         transform matrix from uv to xy
    #     @trans_inv: 3x3 np.array
    #         inverse of trans, transform matrix from xy to uv

    # Matlab:
    # ----------
    # % For a nonreflective similarity:
    # %
    # % let sc = s*cos(theta)
    # % let ss = s*sin(theta)
    # %
    # %                   [ sc -ss
    # % [u v] = [x y 1] *   ss  sc
    # %                     tx  ty]
    # %
    # % There are 4 unknowns: sc,ss,tx,ty.
    # %
    # % Another way to write this is:
    # %
    # % u = [x y 1 0] * [sc
    # %                  ss
    # %                  tx
    # %                  ty]
    # %
    # % v = [y -x 0 1] * [sc
    # %                   ss
    # %                   tx
    # %                   ty]
    # %
    # % With 2 or more correspondence points we can combine the u equations and
    # % the v equations for one linear system to solve for sc,ss,tx,ty.
    # %
    # % [ u1  ] = [ x1  y1  1  0 ] * [sc]
    # % [ u2  ]   [ x2  y2  1  0 ]   [ss]
    # % [ ... ]   [ ...          ]   [tx]
    # % [ un  ]   [ xn  yn  1  0 ]   [ty]
    # % [ v1  ]   [ y1 -x1  0  1 ]
    # % [ v2  ]   [ y2 -x2  0  1 ]
    # % [ ... ]   [ ...          ]
    # % [ vn  ]   [ yn -xn  0  1 ]
    # %
    # % Or rewriting the above matrix equation:
    # % U = X * r, where r = [sc ss tx ty]'
    # % so r = X\U.
    # %
    # """
    options = {'K': 2}

    K = options['K']
    M = xy.shape[0]
    x = xy[:, 0].reshape((-1, 1))  # use reshape to keep a column vector
    y = xy[:, 1].reshape((-1, 1))  # use reshape to keep a column vector
    # print '--->x, y:\n', x, y

    tmp1 = np.hstack((x, y, np.ones((M, 1)), np.zeros((M, 1))))
    tmp2 = np.hstack((y, -x, np.zeros((M, 1)), np.ones((M, 1))))
    X = np.vstack((tmp1, tmp2))
    # print '--->X.shape: ', X.shape
    # print 'X:\n', X

    u = uv[:, 0].reshape((-1, 1))  # use reshape to keep a column vector
    v = uv[:, 1].reshape((-1, 1))  # use reshape to keep a column vector
    U = np.vstack((u, v))
    # print '--->U.shape: ', U.shape
    # print 'U:\n', U

    # We know that X * r = U
    if rank(X) >= 2 * K:
        r, _, _, _ = lstsq(X, U)
        r = np.squeeze(r)
    else:
        raise Exception('cp2tform:twoUniquePointsReq')

    # print '--->r:\n', r

    sc = r[0]
    ss = r[1]
    tx = r[2]
    ty = r[3]

    Tinv = np.array([
        [sc, -ss, 0],
        [ss,  sc, 0],
        [tx,  ty, 1]
    ])

    # print '--->Tinv:\n', Tinv

    T = inv(Tinv)
    # print '--->T:\n', T

    T[:, 2] = np.array([0, 0, 1])

    return T, Tinv


def findSimilarity(uv, xy, options=None):
    # """
    # Function:
    # ----------
    #     Find Reflective Similarity Transform Matrix 'trans':
    #         u = uv[:, 0]
    #         v = uv[:, 1]
    #         x = xy[:, 0]
    #         y = xy[:, 1]
    #         [x, y, 1] = [u, v, 1] * trans

    # Parameters:
    # ----------
    #     @uv: Kx2 np.array
    #         source points each row is a pair of coordinates (x, y)
    #     @xy: Kx2 np.array
    #         each row is a pair of inverse-transformed
    #     @option: not used, keep it as None

    # Returns:
    # ----------
    #     @trans: 3x3 np.array
    #         transform matrix from uv to xy
    #     @trans_inv: 3x3 np.array
    #         inverse of trans, transform matrix from xy to uv

    # Matlab:
    # ----------
    # % The similarities are a superset of the nonreflective similarities as they may
    # % also include reflection.
    # %
    # % let sc = s*cos(theta)
    # % let ss = s*sin(theta)
    # %
    # %                   [ sc -ss
    # % [u v] = [x y 1] *   ss  sc
    # %                     tx  ty]
    # %
    # %          OR
    # %
    # %                   [ sc  ss
    # % [u v] = [x y 1] *   ss -sc
    # %                     tx  ty]
    # %
    # % Algorithm:
    # % 1) Solve for trans1, a nonreflective similarity.
    # % 2) Reflect the xy data across the Y-axis,
    # %    and solve for trans2r, also a nonreflective similarity.
    # % 3) Transform trans2r to trans2, undoing the reflection done in step 2.
    # % 4) Use TFORMFWD to transform uv using both trans1 and trans2,
    # %    and compare the results, Returnsing the transformation corresponding
    # %    to the smaller L2 norm.

    # % Need to reset options.K to prepare for calls to findNonreflectiveSimilarity.
    # % This is safe because we already checked that there are enough point pairs.
    # """
    options = {'K': 2}

#    uv = np.array(uv)
#    xy = np.array(xy)

    # Solve for trans1
    trans1, trans1_inv = findNonreflectiveSimilarity(uv, xy, options)

    # Solve for trans2

    # manually reflect the xy data across the Y-axis
    xyR = xy
    xyR[:, 0] = -1 * xyR[:, 0]

    trans2r, trans2r_inv = findNonreflectiveSimilarity(uv, xyR, options)

    # manually reflect the tform to undo the reflection done on xyR
    TreflectY = np.array([
        [-1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    trans2 = np.dot(trans2r, TreflectY)

    # Figure out if trans1 or trans2 is better
    xy1 = tformfwd(trans1, uv)
    norm1 = norm(xy1 - xy)

    xy2 = tformfwd(trans2, uv)
    norm2 = norm(xy2 - xy)

    if norm1 <= norm2:
        return trans1, trans1_inv
    else:
        trans2_inv = inv(trans2)
        return trans2, trans2_inv


def get_similarity_transform(src_pts, dst_pts, reflective=True):
    # """
    # Function:
    # ----------
    #     Find Similarity Transform Matrix 'trans':
    #         u = src_pts[:, 0]
    #         v = src_pts[:, 1]
    #         x = dst_pts[:, 0]
    #         y = dst_pts[:, 1]
    #         [x, y, 1] = [u, v, 1] * trans

    # Parameters:
    # ----------
    #     @src_pts: Kx2 np.array
    #         source points, each row is a pair of coordinates (x, y)
    #     @dst_pts: Kx2 np.array
    #         destination points, each row is a pair of transformed
    #         coordinates (x, y)
    #     @reflective: True or False
    #         if True:
    #             use reflective similarity transform
    #         else:
    #             use non-reflective similarity transform

    # Returns:
    # ----------
    #    @trans: 3x3 np.array
    #         transform matrix from uv to xy
    #     trans_inv: 3x3 np.array
    #         inverse of trans, transform matrix from xy to uv
    # """

    if reflective:
        trans, trans_inv = findSimilarity(src_pts, dst_pts)
    else:
        trans, trans_inv = findNonreflectiveSimilarity(src_pts, dst_pts)

    return trans, trans_inv


def cvt_tform_mat_for_cv2(trans):
    # """
    # Function:
    # ----------
    #     Convert Transform Matrix 'trans' into 'cv2_trans' which could be
    #     directly used by cv2.warpAffine():
    #         u = src_pts[:, 0]
    #         v = src_pts[:, 1]
    #         x = dst_pts[:, 0]
    #         y = dst_pts[:, 1]
    #         [x, y].T = cv_trans * [u, v, 1].T

    # Parameters:
    # ----------
    #     @trans: 3x3 np.array
    #         transform matrix from uv to xy

    # Returns:
    # ----------
    #     @cv2_trans: 2x3 np.array
    #         transform matrix from src_pts to dst_pts, could be directly used
    #         for cv2.warpAffine()
    # """
    cv2_trans = trans[:, 0:2].T

    return cv2_trans


def get_similarity_transform_for_cv2(src_pts, dst_pts, reflective=True):
    # """
    # Function:
    # ----------
    #     Find Similarity Transform Matrix 'cv2_trans' which could be
    #     directly used by cv2.warpAffine():
    #         u = src_pts[:, 0]
    #         v = src_pts[:, 1]
    #         x = dst_pts[:, 0]
    #         y = dst_pts[:, 1]
    #         [x, y].T = cv_trans * [u, v, 1].T

    # Parameters:
    # ----------
    #     @src_pts: Kx2 np.array
    #         source points, each row is a pair of coordinates (x, y)
    #     @dst_pts: Kx2 np.array
    #         destination points, each row is a pair of transformed
    #         coordinates (x, y)
    #     reflective: True or False
    #         if True:
    #             use reflective similarity transform
    #         else:
    #             use non-reflective similarity transform

    # Returns:
    # ----------
    #     @cv2_trans: 2x3 np.array
    #         transform matrix from src_pts to dst_pts, could be directly used
    #         for cv2.warpAffine()
    # """
    trans, trans_inv = get_similarity_transform(src_pts, dst_pts, reflective)
    cv2_trans = cvt_tform_mat_for_cv2(trans)

    return cv2_trans


if __name__ == '__main__':
    # """
    # u = [0, 6, -2]
    # v = [0, 3, 5]
    # x = [-1, 0, 4]
    # y = [-1, -10, 4]

    # # In Matlab, run:
    # #
    # #   uv = [u'; v'];
    # #   xy = [x'; y'];
    # #   tform_sim=cp2tform(uv,xy,'similarity');
    # #
    # #   trans = tform_sim.tdata.T
    # #   ans =
    # #       -0.0764   -1.6190         0
    # #        1.6190   -0.0764         0
    # #       -3.2156    0.0290    1.0000
    # #   trans_inv = tform_sim.tdata.Tinv
    # #    ans =
    # #
    # #       -0.0291    0.6163         0
    # #       -0.6163   -0.0291         0
    # #       -0.0756    1.9826    1.0000
    # #    xy_m=tformfwd(tform_sim, u,v)
    # #
    # #    xy_m =
    # #
    # #       -3.2156    0.0290
    # #        1.1833   -9.9143
    # #        5.0323    2.8853
    # #    uv_m=tforminv(tform_sim, x,y)
    # #
    # #    uv_m =
    # #
    # #        0.5698    1.3953
    # #        6.0872    2.2733
    # #       -2.6570    4.3314
    # """
    u = [0, 6, -2]
    v = [0, 3, 5]
    x = [-1, 0, 4]
    y = [-1, -10, 4]

    uv = np.array((u, v)).T
    xy = np.array((x, y)).T

    # print '\n--->uv:'
    # print uv
    # print '\n--->xy:'
    # print xy

    trans, trans_inv = get_similarity_transform(uv, xy)

    # print '\n--->trans matrix:'
    # print trans

    # print '\n--->trans_inv matrix:'
    # print trans_inv

    # print '\n---> apply transform to uv'
    # print '\nxy_m = uv_augmented * trans'
    uv_aug = np.hstack((
        uv, np.ones((uv.shape[0], 1))
    ))
    xy_m = np.dot(uv_aug, trans)
    # print xy_m

    # print '\nxy_m = tformfwd(trans, uv)'
    xy_m = tformfwd(trans, uv)
    # print xy_m

    # print '\n---> apply inverse transform to xy'
    # print '\nuv_m = xy_augmented * trans_inv'
    xy_aug = np.hstack((
        xy, np.ones((xy.shape[0], 1))
    ))
    uv_m = np.dot(xy_aug, trans_inv)
    # print uv_m

    # print '\nuv_m = tformfwd(trans_inv, xy)'
    uv_m = tformfwd(trans_inv, xy)
    # print uv_m

    uv_m = tforminv(trans, xy)
    # print '\nuv_m = tforminv(trans, xy)'
    # print uv_m