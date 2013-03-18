import numpy as n
# import pylab as p


def _angle_to_point(point, centre):
    '''calculate angle in 2-D between points and x axis'''
    delta = point - centre
    res = n.arctan(delta[1] / delta[0])
    if delta[0] < 0:
        res += n.pi
    return res


def area_of_triangle(p1, p2, p3):
    '''calculate area of any triangle given co-ordinates of the corners'''
    return n.linalg.norm(n.cross((p2 - p1), (p3 - p1))) / 2.


def convex_hull(points, graphic=False, smidgen=0.0075):
    '''Calculate subset of points that make a convex hull around points

Recursively eliminates points that lie inside two neighbouring points
until only convex hull is remaining.

:Parameters:
    points : ndarray (2 x m)
        array of points for which to find hull
    graphic : bool
        use pylab to show progress?
    smidgen : float
        offset for graphic number labels - useful values
                                           depend on your data range

:Returns:
    hull_points : ndarray (2 x n)
        convex hull surrounding points
'''
    n_pts = points.shape[1]
    assert(n_pts > 5)
    centre = points.mean(1)
    angles = n.apply_along_axis(_angle_to_point, 0, points, centre)
    pts_ord = points[:, angles.argsort()]
    pts = [x[0] for x in zip(pts_ord.transpose())]
    prev_pts = len(pts) + 1
    k = 0
    while prev_pts > n_pts:
        prev_pts = n_pts
        n_pts = len(pts)
        i = -2
        while i < (n_pts - 2):
            Aij = area_of_triangle(centre, pts[i], pts[(i + 1) % n_pts])
            Ajk = area_of_triangle(centre, pts[(i + 1) % n_pts],
                                   pts[(i + 2) % n_pts])
            Aik = area_of_triangle(centre, pts[i], pts[(i + 2) % n_pts])
            if Aij + Ajk < Aik:
                del pts[i + 1]
            i += 1
            n_pts = len(pts)
        k += 1
    return n.asarray(pts)

if __name__ == "__main__":
    import pylab
    points = n.random.random_sample((2, 40))
    hull_pts = convex_hull(points)

    print points
    print hull_pts
    for i in range(40):
        pylab.plot(points[0][i], points[1][i], "ro")
    for i in hull_pts:
        pylab.plot(i[0], i[1], "bx")
    pylab.show()
