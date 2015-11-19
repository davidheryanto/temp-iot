//var serverEndpoint = "http://makan.iprekt.com:9999";
var serverEndpoint = "http://sga81109:5000";
var selectDateRange, tabTimeSeries,
    map, marker, routeLine;

var chartTimeSeries = null;
var chartHeight = 270;
var chartScoreOptions = {
    chart: {
        polar: true,
        type: 'line',
        height: chartHeight
    },

    title: null,

    pane: {
        size: '80%'
    },

    legend: {
        enabled: false
    },

    xAxis: {
        categories: ['Distance', 'Harsh Break', 'Sudden Turn', 'Harsh Accel', 'Speed'],
        tickmarkPlacement: 'on',
        lineWidth: 0
    },

    yAxis: {
        gridLineInterpolation: 'polygon',
        lineWidth: 0,
        min: 0,
        max: 100
    },

    tooltip: {
        shared: true,
        pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>'
    },

    series: [{
        name: 'Score',
        data: [4, 5, 4.2, 4.5, 2.6],
        pointPlacement: 'on'
    }]
};

Highcharts.setOptions({
    chart: {
        style: {
            fontFamily: 'Helvetica'
        }
    },
    yAxis: {
        min: 0
    }
});


$(document).ready(function () {
    init();
});


function init() {
    // Defaults
    selectDateRange = 30;  // Default to one month
    tabTimeSeries = $("a[href$='#score']");

    setupEventHandlers();
    getChartOptions(tabTimeSeries, plotChart);

    updateScoreBreakdown("#driver-score-chart", function () {
        $("#alert-driver").slideDown()
    });

}

function updateScoreBreakdown(chartDiv, callback) {
    var $overallScore = $("#div-overall-score").empty()
        .css("height", chartHeight)
        .css("text-align", "center");
    $overallScore.append($("<img/>", {
        src: "img/loading_spinner.gif",
        "class": "loading"
    }));


    var $chartDiv = $(chartDiv).empty()
        .css("height", chartHeight)
        .css("text-align", "center")
        .css("padding-top", 30);
    $chartDiv.append($("<img/>", {
        src: "img/loading_spinner.gif",
        "class": "loading"
    }));
    $.ajax({
        url: serverEndpoint + "/score/" + selectDateRange,
        success: function (data) {
            chartScoreOptions.series[0].data = data["score"];
            $chartDiv.highcharts(chartScoreOptions);

            // Update overall score
            var d = data["score"];
            var sum = 0;
            for (var i = 0, l = d.length; i < l; i++) {
                sum += parseInt(d[i]);
            }
            var avg = sum / l;
            var scoreDial = $("<input/>", {
                "class": "dial",
                "type": "text",
                "value": avg
            });
            $overallScore.empty().append(scoreDial);
            $(".dial").knob({
                readOnly: true
            });

            if (callback) {
                setTimeout(callback, 2000);
            }
        }
    })
}

function initMap() {
    // https://developers.google.com/maps/documentation/javascript/tutorial
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 1.385244, lng: 102.851920},
        zoom: 12,
        streetViewControl: false,
        mapTypeControl: false
    });
    setTimeout(updateMap, 3000);
}

function updateMap() {
    // curLoc = [lat,lng]
    // routes = [[lat,lng],[lat,lng]...]
    if (map === undefined || selectDateRange === undefined) {
        return;
    }

    $.ajax({
        url: serverEndpoint + "/timeseries/Location/" + selectDateRange,
        success: function (data) {
            console.log(serverEndpoint + "/timeseries/Location/" + selectDateRange);
            console.log(data);
            var seriesData = data["series"];

            if (seriesData.length <= 0) {
                return;
            }

            // Put a marker for current lcoation
            var currentLocation = {
                lat: seriesData[seriesData.length - 1][1]["latitude"],
                lng: seriesData[seriesData.length - 1][1]["longitude"]
            };
            if (marker === undefined) {
                marker = new google.maps.Marker({
                    position: currentLocation,
                    map: map
                });
            } else {
                marker.setPosition(new google.maps.LatLng(currentLocation.lat, currentLocation.lng));
            }
            map.panTo(new google.maps.LatLng(currentLocation.lat, currentLocation.lng));

            // Draw route line for past locations
            var routes = [];
            seriesData.forEach(function (item) {
                var location = {
                    lat: item[1]["latitude"],
                    lng: item[1]["longitude"]
                };
                console.log(location);
                routes.push(location);
            });

            if (routeLine === undefined) {
                routeLine = new google.maps.Polyline({
                    path: routes,
                    geodesic: true,
                    strokeColor: '#003466',
                    strokeOpacity: 0.75,
                    strokeWeight: 2.5
                });
                routeLine.setMap(map);
            } else {
                routeLine.setPath(routes);
            }

        }
    })
}

function setupEventHandlers() {
    // When date range is changed
    $("#select-date-range").on("change", function (e) {
        selectDateRange = this.value;
        getChartOptions(tabTimeSeries, plotChart);
        updateMap();

        // Replot score
        updateScoreBreakdown("#driver-score-chart");
    });

    // When tab in timeries is clicked
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
        tabTimeSeries = e.target;
        getChartOptions(tabTimeSeries, plotChart)
    })
}

function getChartOptions(targetDiv, callback) {
    var $targetDiv = $(targetDiv);
    var propertyName = $targetDiv.data("property-name");
    var chartDiv = $($targetDiv.attr("href") + " .chart-stage").empty()
        .css("height", chartHeight)
        .css("text-align", "center");
    chartDiv.append($("<img/>", {
        src: "img/loading_spinner.gif",
        "class": "loading"
    }));
    $.ajax({
        url: serverEndpoint + "/timeseries/" + propertyName + "/" + selectDateRange,
        success: function (data) {
            callback(data["series"], propertyName, chartDiv);
        }
    })
}


function plotChart(series, propertyName, chartDiv) {
    var chartOptions = {
        'chart': {'zoomType': 'x'},
        'title': {'text': propertyName + ' Over Time'},
        'xAxis': {'type': 'datetime'},
        'yAxis': {'title': {'text': propertyName}},
        'legend': {'enabled': false},
        'series': [{
            'name': propertyName,
            'data': series
        }]
    };

    // For score, use diff color for diff value
    if (propertyName === 'Score') {
        chartOptions["series"][0]["zones"] =
            [
                {
                    'value': 50,
                    'color': '#FC8662'
                },
                {
                    'value': 75,
                    'color': '#FADE25'
                },
                {
                    'color': '#ADF005'
                }
            ];
    }


    chartOptions['chart']['height'] = chartHeight;
    chartTimeSeries = chartDiv.highcharts(chartOptions);
}


