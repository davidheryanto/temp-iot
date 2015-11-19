import ast
import json
import random
import time
from datetime import datetime, timedelta

import numpy as np
import requests
from flask import Flask, jsonify
from flask.ext.autodoc import Autodoc
from flask.ext.cors import CORS
from flask_swagger import swagger

from data_generator import generate_data, generate_location

atrack_service_url = ('http://ge2-1667.cloud.thingworx.com/Thingworx/Things'
                      '/ATrack%20RemoteThing/Services')
app_key = "74dcc94c-ee5d-4737-a57f-11422d76e774"

app = Flask(__name__)
cors = CORS(app)
auto = Autodoc(app)

default_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'AppKey': app_key
}


# default_proxies = {
#     'http': 'http://proxy.sg.kworld.kpmg.com:8080',
#     'https': 'http://proxy.sg.kworld.kpmg.com:8080'
# }


def create_poisson_series(lam, n_prev_day, interval_minutes=360, max_val=None):
    from datetime import datetime, timedelta
    import time
    import numpy as np

    def timestamp(dt):
        return int(time.mktime(dt.timetuple()) * 1000)

    cur_datetime = datetime.today()
    timestamps = [timestamp(cur_datetime)]
    n_prev_30min = n_prev_day * 24 * 2
    for _ in range(n_prev_30min):
        cur_datetime = cur_datetime - timedelta(minutes=interval_minutes)
        timestamps.append(timestamp(cur_datetime))
    pvals = np.random.poisson(lam, len(timestamps))
    if max_val:
        pvals = [min(max_val, x) for x in pvals]
    series_data = [[x, y] for (x, y) in zip(timestamps, pvals)]
    return series_data


def query_property_history_by_name_thingworx(property_name, n_prev_day):
    url = atrack_service_url + '/QueryNamedPropertyHistory'
    prev_datetime = datetime.today() - timedelta(days=n_prev_day)
    prev_timestamp = int(time.mktime(prev_datetime.timetuple()) * 1000)
    data = {
        'propertyNames': {
            'dataShape': {
                'fieldDefinitions': {
                    'name': {
                        'name': 'name',
                        'baseType': 'STRING'
                    }
                }
            },
            'rows': [
                {
                    'name': str(property_name)
                }
            ],
        },
        'startDate': prev_timestamp,
        'maxItems': 5000
    }
    # resp = requests.post(url, headers=default_headers, proxies=default_proxies,
    #                      data=json.dumps(data))
    resp = requests.post(url, headers=default_headers, data=json.dumps(data))
    result = ast.literal_eval(resp.text)
    series_data = [(x["timestamp"], x[property_name]) for x in result['rows']]
    return series_data


def score_speed(speed):
    if speed < 30:
        return 100
    elif speed < 50:
        return 70
    elif speed < 75:
        return 50
    else:
        return 30


def score_day_dist(dist):
    if dist < 5:
        return 100
    elif dist < 10:
        return 70
    elif dist < 20:
        return 50
    else:
        return 30


@app.route('/documentation')
def documentation():
    return auto.html()


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = '0.1'
    swag['info']['title'] = 'ATrack API'
    return jsonify(swag)


@app.route('/timeseries')
def query_property_history():
    url = atrack_service_url + '/QueryPropertyHistory'
    resp = requests.post(url, headers=default_headers, proxies=default_proxies)
    result = ast.literal_eval(resp.text)
    return jsonify(result)


@app.route('/score/<int:n_prev_day>', methods=['GET'])
@auto.doc()
def query_score(n_prev_day):
    """
    Get each driver score parameter
    :param n_prev_day: <last n_prev_day> day score will be returned
    :return: {"score": [<distance_score>,
                        <harsh_break_score>,
                        <sudden_turn_score>,
                        <harsh_accel_score>,
                        <speed_score>]
            }
    """
    # Get the speed series
    if n_prev_day < 4:
        start_val = random.randrange(20, 30)
    elif n_prev_day < 7:
        start_val = random.randrange(30, 35)
    elif n_prev_day < 14:
        start_val = random.randrange(35, 40)
    else:
        start_val = 30
    speed_series = generate_data(start_val, 0, 120, n_prev_day, 120, [
        [datetime.now() - timedelta(days=21), 0.4, 1.0],
        [datetime.now() - timedelta(days=20), 0.1, 0.3],
        [datetime.now() - timedelta(days=10), -1.0, 0.5],
        [datetime.now() - timedelta(days=7), 0.3, 1.2],
        [datetime.now() - timedelta(days=5), -0.8, 0.5],
        [datetime.now() - timedelta(days=4), 0.3, 0.2],
        [datetime.now() - timedelta(days=2), 3, 1.3]
    ])
    speed_scores = [score_speed(s[1]) for s in speed_series]
    speed_score = np.average(speed_scores)
    print('SPEED_SCORE: {}'.format(speed_score))

    # Get the odometer series
    if n_prev_day < 4:
        start_val = random.randrange(0, 20)
    elif n_prev_day < 7:
        start_val = random.randrange(20, 50)
    elif n_prev_day < 14:
        start_val = random.randrange(50, 120)
    else:
        start_val = 120
    odomoter_series = generate_data(start_val, 0, 1000, n_prev_day, 120, [
        [datetime.now() - timedelta(days=21), 2, 1.0],
        [datetime.now() - timedelta(days=20), 0.5, 0.3],
        [datetime.now() - timedelta(days=10), 2, 0.5],
        [datetime.now() - timedelta(days=7), 2, 1],
        [datetime.now() - timedelta(days=5), 3.5, 1],
        [datetime.now() - timedelta(days=2), 3.5, 2.0]
    ])
    odomoter_series_sorted = sorted(odomoter_series, key=lambda x: x[0],
                                    reverse=True)

    day_dist_series = []
    odo_iter = iter(odomoter_series_sorted)
    day = 1
    cur_odo = next(odo_iter)
    while day <= n_prev_day:
        try:
            next_odo = next(odo_iter)
        except StopIteration:
            break

        day_diff = (datetime.fromtimestamp(cur_odo[0] / 1000) -
                    datetime.fromtimestamp(next_odo[0] / 1000)).days
        if day_diff == 1:
            day += 1
            day_dist_series.append(
                (cur_odo[1] - next_odo[1]))
            cur_odo = next_odo

    if len(day_dist_series) < 1 or len(day_dist_series) < n_prev_day:
        day_dist_series.append((cur_odo[1] - next_odo[1]) / 10.0)
    day_dist_scores = [score_day_dist(x) for x in day_dist_series]
    day_dist_score = np.average(day_dist_scores)

    # Array order
    # 'Distance', 'Harsh Break', 'Sudden Turn', 'Harsh Accel', 'Speed'
    def rand_score():
        return random.randrange(50, 100)

    if n_prev_day < 2:
        speed_score = max(10, speed_score - 45)
        day_dist_score = max(12, day_dist_score - 45)
        a, b, c = rand_score() - 40, rand_score() - 30, rand_score() - 35
    elif n_prev_day < 4:
        speed_score = max(15, speed_score - 40)
        day_dist_score = max(15, day_dist_score - 40)
        a, b, c = rand_score() - 25, rand_score() - 20, rand_score() - 30
    elif n_prev_day < 8:
        speed_score = max(20, speed_score - 30)
        day_dist_score = max(25, day_dist_score - 30)
        a, b, c = rand_score() - 10, rand_score() - 10, rand_score() - 10
    else:
        speed_score = max(20, speed_score - 12)
        day_dist_score = max(25, day_dist_score - 12)
        a, b, c = rand_score(), rand_score(), rand_score()

    return jsonify({'score': [day_dist_score, a, b, c, speed_score]})


@app.route('/timeseries/<property_name>/<int:n_prev_day>', methods=['GET'])
@auto.doc()
def query_property_history_by_name(property_name, n_prev_day):
    """
    Get the historical values for the car status property
    :param property_name: status property, currently accept: Score, Speed, Odometer or Location
    :param n_prev_day: <last n_prev_day> day values will be returned
    :return:
    if property_name is Location:
      {"series": [ [<timestamp>,{"latitude": <float_val>, "longitude": <float_val>}], ... ] }
    else:
      {"series": [ [<timestamp>, <value>], ...] }
    """
    if property_name == 'Score':
        if n_prev_day < 4:
            start_val = random.randrange(30, 36)
        elif n_prev_day < 7:
            start_val = random.randrange(36, 41)
        elif n_prev_day < 14:
            start_val = random.randrange(40, 61)
        else:
            start_val = 75
        series_data = generate_data(start_val, 0, 100, n_prev_day, 120, [
            [datetime.now() - timedelta(days=21), 0.4, 1.0],
            [datetime.now() - timedelta(days=10), -0.1, 0.5],
            [datetime.now() - timedelta(days=14), -0.4, 0.3],
            [datetime.now() - timedelta(days=7), -0.8, 0.3],
            [datetime.now() - timedelta(days=2), -1.5, 0.4]
        ])
    elif property_name == 'Speed':
        print('SPEED')
        if n_prev_day < 4:
            start_val = random.randrange(20, 30)
        elif n_prev_day < 7:
            start_val = random.randrange(30, 35)
        elif n_prev_day < 14:
            start_val = random.randrange(35, 40)
        else:
            start_val = 30
        series_data = generate_data(start_val, 0, 120, n_prev_day, 120, [
            [datetime.now() - timedelta(days=21), 0.4, 1.0],
            [datetime.now() - timedelta(days=20), 0.1, 0.3],
            [datetime.now() - timedelta(days=10), -1.0, 0.5],
            [datetime.now() - timedelta(days=7), 0.3, 1.2],
            [datetime.now() - timedelta(days=5), -0.8, 0.5],
            [datetime.now() - timedelta(days=4), 0.3, 0.2],
            [datetime.now() - timedelta(days=2), 3, 1.3]
        ])
    elif property_name == 'Odometer':
        if n_prev_day < 4:
            start_val = random.randrange(0, 20)
        elif n_prev_day < 7:
            start_val = random.randrange(20, 50)
        elif n_prev_day < 14:
            start_val = random.randrange(50, 120)
        else:
            start_val = 120
        series_data = generate_data(start_val, 0, 1000, n_prev_day, 120, [
            [datetime.now() - timedelta(days=21), 2, 1.0],
            [datetime.now() - timedelta(days=20), 0.5, 0.3],
            [datetime.now() - timedelta(days=10), 2, 0.5],
            [datetime.now() - timedelta(days=7), 2, 1],
            [datetime.now() - timedelta(days=5), 3.5, 1],
            [datetime.now() - timedelta(days=2), 3.5, 2.0]
        ])
    elif property_name == 'Location':
        series_data = generate_location(n_prev_day)
    else:
        lam = min(random.random(), 0.005)
        series_data = create_poisson_series(lam=lam, n_prev_day=n_prev_day)

    # series_data_sorted = sorted(series_data, key=lambda x: x[0])
    # if property_name == 'Odometer':
    #     property_name = 'Distance (km)'
    # elif property_name == 'Speed':
    #     property_name = 'Max Speed (km/h)'
    # elif property_name == 'HarshBrake':
    #     property_name = 'Harsh Brake'
    # elif property_name == 'SuddenTurn':
    #     property_name = 'Sudden Turn'
    #
    # chart_options = {
    #     'chart': {'zoomType': 'x'},
    #     'title': {'text': property_name + ' Over Time'},
    #     'xAxis': {'type': 'datetime'},
    #     'yAxis': {'title': {'text': property_name}},
    #     'legend': {'enabled': False},
    #     'series': [{'name': property_name,
    #                 'data': series_data_sorted}]
    # }
    #
    # # For score color the chart differently for diff y-axis
    # if property_name == 'Score':
    #     chart_options["series"][0].update(
    #         {'zones': [
    #             {
    #                 'value': 50,
    #                 'color': '#FC8662'
    #             },
    #             {
    #                 'value': 75,
    #                 'color': '#FADE25'
    #             },
    #             {
    #                 'color': '#ADF005'
    #             }
    #         ]}
    #     )
    #
    # if property_name == 'Score':
    #     chart_options['yAxis'].update({'max': 100})

    return jsonify({"series": series_data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
