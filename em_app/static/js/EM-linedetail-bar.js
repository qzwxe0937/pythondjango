function setEMLineDetailBarChart(labels, defaultValueG, defaultValueY, defaultValueR) {
    // Set new default font family and font color to mimic Bootstrap's default styling
    // Bar Chart Example
    var ctx = document.getElementById("EMLineDetailBarChart");
    var myLineChart = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: [{
                label: "G",
                backgroundColor: "#00FF00",
                data: defaultValueG,
            }, {
                label: "Y",
                backgroundColor: "#FFFF00",
                data: defaultValueY,
            }, {
                label: "R",
                backgroundColor: "#FF0000",
                data: defaultValueR,
            }],
        },
        options: {
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        fontSize: 10
                    }
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        fontSize: 10
                    }
                }]
            }
        }
    });
}

function setEMLineDetailBarChartWithPercentage(labels, defaultValueG, defaultValueY, defaultValueR) {
    var oringinValueG = defaultValueG.slice();
    var oringinValueY = defaultValueY.slice();
    var oringinValueR = defaultValueR.slice();

    Chart.pluginService.register({
        beforeInit: function (chartInstance) {

            var totals = [];
            chartInstance.data.datasets.forEach(function (dataset) {
                for (var i = 0; i < dataset.data.length; i++) {
                    var total = 0;
                    chartInstance.data.datasets.forEach(function (dataset) {
                        total += dataset.data[i];
                    });
                    totals.push(total);
                }
            });

            chartInstance.data.datasets.forEach(function (dataset) {
                for (var i = 0; i < dataset.data.length; i++) {
                    dataset.data[i] = '' + (dataset.data[i] / totals[i]) * 100;
                }
            });

        },

        afterDraw: function (chartInstance) {
            var ctx = chartInstance.chart.ctx;

            ctx.font = Chart.helpers.fontString(20, 'normal', Chart.defaults.global.defaultFontFamily);
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            ctx.fillStyle = 'black';

            chartInstance.data.datasets.forEach(function (dataset) {
                //if (dataset._meta[0].controller.index != 0) return;
                for (var i = 0; i < dataset.data.length; i++) {
                    if (dataset.data[i] > 0) {
                        var model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                        //if (dataset.label == "G"){
                        //    ctx.fillText(oringinValueG[i], ((model.base + model.x) / 2), (model.y + model.height / 5));
                        //} else if (dataset.label == "Y") {
                        //    ctx.fillText(oringinValueY[i], ((model.base + model.x) / 2), (model.y + model.height / 5));
                        //} else if (dataset.label == "R") {
                        //    ctx.fillText(oringinValueR[i], ((model.base + model.x) / 2), (model.y + model.height / 5));
                        //}
                        ctx.fillText(parseFloat(dataset.data[i]).toFixed(0) + "%", ((model.base + model.x) / 2), (model.y + model.height / 3));
                    }
                }
            });

        }
    });

    var priceComplianceData = {
        labels: labels,
        datasets: [{
            label: "暫不需保養",
            backgroundColor: "#00FF00",
            hoverBackgroundColor: "#00FF00",
            data: defaultValueG
        }, {
            label: "即將過期",
            backgroundColor: "#FFFF00",
            hoverBackgroundColor: "#FFFF00",
            // The vals below have been multiplied by 10 (a 0 appended) so that the values are at least visible to the naked eye
            data: defaultValueY
        }, {
            label: "已過期",
            backgroundColor: "#FF0000",
            hoverBackgroundColor: "#FF0000",
            // The vals below have been multiplied by 10 (a 0 appended) so that the values are at least visible to the naked eye
            data: defaultValueR
        }]
    };

    var priceComplianceOptions = {
        legend: {
            labels: {
                fontSize: 20,
                fontFamily: '微軟正黑體'
            }
        },
        scales: {
            xAxes: [{
                stacked: true,
                ticks: {
                    min: 0,
                    max: 100,
                    callback: function (value) {
                        return value + "%"
                    }
                },
            }],
            yAxes: [{
                stacked: true,
                ticks: {
                    fontSize: 20, 
                    fontFamily: '微軟正黑體'
                }
            }]
        },
        tooltips: {
            enabled: false
        }
    };

    var ctxBarChart = document.getElementById("EMLineDetailBarChart");
    var priceBarChart = new Chart(ctxBarChart, {
        type: 'horizontalBar',
        data: priceComplianceData,
        options: priceComplianceOptions
    });
}