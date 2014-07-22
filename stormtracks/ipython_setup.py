# Puts some interesting objects in an ipython interactive shell
# Should be run using e.g.:
#
# In [1]: run ipython_setup.py
import sys
import time
import datetime as dt
import socket

import numpy as np
import pylab as plt

import c20data as c
import tracking as t
import match as m
import plotting as pl
import utils.kalman as k
from ibtracsdata import IbtracsData

# num_ensemble_members = 56
num_ensemble_members = 3

start = time.time()
print(start)

short_name = socket.gethostname().split('.')[0]

if short_name == 'linz':
    ensemble_member_range = range(0, 3)
elif short_name == 'athens':
    sys.exit('bad computer')
    ensemble_member_range = range(3, 6)
elif short_name == 'madrid':
    ensemble_member_range = range(6, 9)
elif short_name == 'warsaw':
    ensemble_member_range = range(9, 12)
elif short_name == 'prague':
    ensemble_member_range = range(12, 15)
elif short_name == 'berlin':
    ensemble_member_range = range(15, 18)
elif short_name == 'determinist-mint':
    ensemble_member_range = range(0, 1)
else:
    ensemble_member_range = range(0, num_ensemble_members)

itd = IbtracsData()
best_tracks = itd.load_ibtracks_year(2005)
c20data = c.C20Data(2005, verbose=False, pressure_level='995')
all_good_matches = []

for i in ensemble_member_range:
    print('Ensemble member {0} of {1}'.format(i + 1, len(ensemble_member_range)))
    gdata = c.GlobalEnsembleMember(c20data, i)
    vort_finder = t.VortmaxFinder(gdata)

    vort_finder.find_vort_maxima(dt.datetime(2005, 6, 1), dt.datetime(2005, 12, 1))
    tracker = t.VortmaxNearestNeighbourTracker()
    tracker.track_vort_maxima(vort_finder.vortmax_time_series)

    matches = m.match(tracker.vort_tracks_by_date, best_tracks)
    good_matches = [ma for ma in matches.values() if ma.av_dist() < 5 and ma.overlap > 6]
    all_good_matches.append(good_matches)

end = time.time()

combined_matches = m.combined_match(best_tracks, all_good_matches)

if False:
    gm2 = good_matches[2]
    pos = np.array([vm.pos for vm in gm2.vort_track.vortmaxes])
    x, P, y = k._demo_simple_2d_with_inertia(pos[0], pos, 1e-1, 1e1)
    plt.clf()
    plt.plot(gm2.best_track.lons, gm2.best_track.lats, 'r-')
    plt.plot(pos[:, 0], pos[:, 1], 'k+')
    plt.plot(x[:, 0], x[:, 1])

print('{0} - {1}'.format(short_name, ensemble_member_range))
print('Start: {0}, end: {1}, duration: {2}'.format(start, end, end - start))
