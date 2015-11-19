import pylab
import matplotlib.pyplot as plt
import random
import copy
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

coords = [[1.340585, 103.709083],
          [1.344698, 103.725971],
          [1.312011, 103.768266],
          [1.312516, 103.776494],


            [1.3136795462688007, 103.77693076979746],
 [1.3106588151831027, 103.76794409256598],
 [1.3426590417840911, 103.72843857586162],
 [1.3377760779105756, 103.70228082990971],

          [1.337837882613404, 103.70981855064188],
 [1.3445595354968167, 103.727808355056],
 [1.3104017306904048, 103.76789634265606],
 [1.3124088279453427, 103.77828684448326],



          [1.307754, 103.785227],
          [1.307826, 103.790929],
          [1.292240, 103.808395],
          [1.290581, 103.832140],
          [1.288272, 103.841523],
          [1.300899, 103.843327],
          [1.306599, 103.840080],
          [1.316846, 103.847369],
          [1.327236, 103.861516],


            [1.3264694605930556, 103.86234886407044],
 [1.3162862401047148, 103.84621068333142],
 [1.3085104757034411, 103.84038844241563],
 [1.301169291049649, 103.84742752394848],
 [1.2878949938093491, 103.84152509398302],
 [1.2889259479690753, 103.83256325331473],
 [1.2924197289985166, 103.8065175453379],
 [1.3085623509914108, 103.79167769514699],
 [1.3106678673736543, 103.78796343646863],
 [1.313583112364666, 103.77770850661106],
 [1.3103904308080436, 103.77105892053807],
 [1.3447414375311806, 103.72438537410544],
 [1.3390175984027672, 103.71036278726136],
[1.339922638114228, 103.70870393904654],
 [1.344618896800464, 103.72859831389145],
 [1.3148737999826572, 103.76769667053037],
 [1.3121001345617553, 103.7756139311843],
 [1.3123126430041754, 103.78398795466576],
 [1.305719302181311, 103.79259515224575],
 [1.2919000480541116, 103.80976731374926],
 [1.2905922702114638, 103.83126043915337],
 [1.282321464963285, 103.84246884169357],
 [1.2997628142275708, 103.84216854754561],
 [1.311781897155682, 103.84191452760722],
 [1.316365670167008, 103.8471857782107],
 [1.3270122127394688, 103.85889607856909],




          [1.353861, 103.856824],
          [1.369477, 103.860780],
          [1.371883, 103.867199],
          [1.369995, 103.876362],
          [1.366896, 103.889682],
          [1.363072, 103.892786],
          [1.359031, 103.893147],
          [1.349651, 103.889682],
          [1.341209, 103.891703],
          [1.328726, 103.905272],
          [1.318985, 103.905055],
          [1.302317, 103.910468],
        [1.312039, 103.948855],
          [1.336673, 103.979565],
          [1.341648, 103.970461],
          [1.349657, 103.964028],
          [1.350507, 103.957959],
          [1.335217, 103.938052],
[1.335702, 103.927613],
          [1.323082, 103.890834],
          [1.319811, 103.876779],
          [1.328014, 103.868439],
          [1.330441, 103.862157],

[1.329027299725381, 103.86059661076611],
 [1.3556439709464034, 103.85730150761694],
 [1.3690242875958787, 103.86146179944657],
 [1.3699128762592117, 103.86544515010051],
 [1.3700807038748293, 103.87796353199882],
 [1.3683804911173245, 103.88878070481677],
 [1.3634269241763293, 103.89498036637275],
 [1.3570858616330925, 103.89059038552377],
 [1.352888371494468, 103.88909495631967],
 [1.343583876627577, 103.88824626326497],
 [1.3295821877751992, 103.90412413073756],
 [1.317520406611572, 103.90987929680479],
 [1.3001274858059058, 103.90634934552342],
 [1.3158750212257841, 103.9481429135692],
 [1.3376896407597485, 103.97448352875128],
 [1.3416803390870657, 103.9700924278707],
 [1.3496062803285565, 103.96633818856377],
 [1.3481713140150258, 103.95912254115545],
 [1.3352723739626973, 103.93193149948884]

          ]


def ts(dt):
    return int(time.mktime(dt.timetuple()) * 1000)


def generate_location(n_day_past, minutes_interval=60,
                      mean_change=0.001, std_change=0.0001):
    start_time = datetime.today() - timedelta(days=n_day_past)
    cur_time = start_time
    out = []

    if n_day_past < 2:
        count = 4
    elif n_day_past < 4:
        count = 14
    elif n_day_past < 7:
        count = 28
    elif n_day_past < 14:
        count = 60
    else:
        count = len(coords)

    i = 0
    while datetime.today() >= cur_time and i < count:
        out.append([ts(cur_time), {'latitude': coords[i][0],
                                   'longitude': coords[i][1]}])
        i += 1
        cur_time += timedelta(minutes=minutes_interval)
        logger.info('{:=^50}'.format(' LOCATION '))
        logger.info('Location length: {}'.format(len(out)))
        logger.info(out[:30])
        logger.info(out[-30:])
        logger.info('{:=^50}'.format(' LOCATION '))
    return out


def generate_data(start_val,
                  min_val,
                  max_val,
                  n_day_past,
                  minutes_interval,
                  changes):
    start_time = datetime.today() - timedelta(days=n_day_past)
    cur_time = start_time
    cur_val = start_val
    out = [[ts(cur_time), cur_val]]

    changes_cp = copy.deepcopy(changes)
    logger.debug(cur_time)
    logger.debug(changes_cp[0][0])
    change = [None, 0, 1.0]  # Default change
    while len(changes_cp) > 0 and cur_time >= changes_cp[0][0]:
        change = changes_cp.pop(0)
    mean_change, std_change = change[1], change[2]

    logger.debug(cur_time)
    while datetime.today() >= cur_time:
        delta = random.normalvariate(mean_change, std_change)
        cur_val += delta
        cur_val = max(min_val, cur_val)
        logger.debug('max:{},cur:{}'.format(max_val, cur_val))
        cur_val = min(max_val, cur_val)
        cur_time += timedelta(minutes=minutes_interval)
        out.append([ts(cur_time), cur_val])
        if len(changes_cp) > 0 and cur_time >= changes_cp[0][0]:
            change = changes_cp.pop(0)
            mean_change, std_change = change[1], change[2]

    logger.debug(out[:10])
    logger.debug(out[-10:])
    # plt.plot([x[0] for x in out], [x[1] for x in out])
    # plt.xlabel('Time')
    # plt.ylabel('Value')
    # plt.show()
    return out


def main():
    duration = 100
    meanIncrease = -0.2
    stDevIncrease = 1.2

    ## Here we generate a fictional time series, for a
    ## variable that generally increases over time but
    ## has significant noise.

    x = range(duration)
    y = []
    yNow = 100

    for i in x:
        nextDelta = random.normalvariate(meanIncrease, stDevIncrease)
        yNow += nextDelta
        y.append(yNow)

    pylab.plot(x, y)
    pylab.xlabel("Time")
    pylab.ylabel("Value")
    pylab.show()


if __name__ == '__main__':
    # generate_data(start_val=0,
    #               min_val=0,
    #               max_val=100,
    #               n_day_past=2,
    #               minutes_interval=30,
    #               changes=[
    #                   [datetime.now() - timedelta(days=7), 0.2, 1.2],
    #                   [datetime.now() - timedelta(days=4), -0.1, 1.2],
    #                   [datetime.now() - timedelta(days=2), -0.1, 0.6],
    #                   [datetime.now() - timedelta(days=1), 0.3, 1.0]
    #               ])
    generate_location(7)
