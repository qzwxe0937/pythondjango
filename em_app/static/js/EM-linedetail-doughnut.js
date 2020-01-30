function setEMLineDetailDoughnut(labels, defaultValue) {
	Chart.pluginService.register({
		beforeDraw: function (chart) {
			if (chart.config.options.elements.center) {
				//Get ctx from string
				var ctx = chart.chart.ctx;

				//Get options from the center object in options
				var centerConfig = chart.config.options.elements.center;
				var fontStyle = centerConfig.fontStyle || 'Arial';
				var txt = centerConfig.text;
				var color = centerConfig.color || '#000';
				var sidePadding = centerConfig.sidePadding || 20;
				var sidePaddingCalculated = (sidePadding / 100) * (chart.innerRadius * 2)
				//Start with a base font of 30px
				ctx.font = "30px " + fontStyle;

				//Get the width of the string and also the width of the element minus 10 to give it 5px side padding
				var stringWidth = ctx.measureText(txt).width;
				var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;

				// Find out how much the font can grow in width.
				var widthRatio = elementWidth / stringWidth;
				var newFontSize = Math.floor(30 * widthRatio);
				var elementHeight = (chart.innerRadius * 2);

				// Pick a new font size so it will not be larger than the height of label.
				var fontSizeToUse = Math.min(newFontSize, elementHeight);

				//Set font settings to draw it correctly.
				ctx.textAlign = 'center';
				ctx.textBaseline = 'middle';
				var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
				var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
				ctx.font = fontSizeToUse + "px " + fontStyle;
				ctx.fillStyle = color;

				//Draw text in center
				ctx.fillText(txt, centerX, centerY);
			}
		}
	});

	var config = {
		type: 'doughnut',
		data: {
			labels: labels,
			datasets: [{
				data: defaultValue,
				backgroundColor: [
					"#00FF00",
					"#FFFF00",
					"#FF0000"
				],
				hoverBackgroundColor: [
					"#00FF00",
					"#FFFF00",
					"#FF0000"
				]
			}]
		},
		options: {
			elements: {
				center: {
					text: arrToPercent(defaultValue),
					color: '#000000', // Default is #000000
					fontStyle: 'Arial', // Default is Arial
					sidePadding: 20 // Defualt is 20 (as a percentage)
				}
			}
		}
	};

	var ctx = document.getElementById("EMLineDetailDoughnut").getContext("2d");
	var myChart = new Chart(ctx, config);
}

function arrToPercent(valueArr) {
	var point = (valueArr[0] + valueArr[1]) / valueArr.reduce(function (a, b) { return a + b; }, 0);
	var str = Number(point * 100).toFixed(2);
	str += "%";
	return str;
}

function setEMLineDetailDoughnutWithLabel(labels, defaultValue) {
	Chart.plugins.register({
		afterDatasetsDraw: function (chartInstance, easing) {
			if (chartInstance.config.type == "doughnut") {
				var ctx = chartInstance.chart.ctx;
				var sum = 0;
				var okPercent
				var okPercentString
				chartInstance.data.datasets.forEach(function (dataset, i) {
					var meta = chartInstance.getDatasetMeta(i);
					if (!meta.hidden) {
						meta.data.forEach(function (element, index) {
							if (dataset.data[index] > 0) {
								ctx.fillStyle = 'black';

								var fontSize = 30;
								var fontStyle = 'normal';
								var fontFamily = 'Arial';
								ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);


								var dataString = chartInstance.data.labels[index];
								var dataString2 = dataset.data[index];

								ctx.textAlign = 'center';
								ctx.textBaseline = 'middle';

								var padding = 5;
								var position = element.tooltipPosition();

								// ctx.fillText(dataString, position.x, position.y - (fontSize / 2) - padding);

								ctx.fillText(dataString2, position.x, position.y - (fontSize / 2) - padding + fontSize);

								// 円の中心に表示する合計を集計する
								sum += dataset.data[index];
							}
						});
						okPercent = (dataset.data[0] + dataset.data[1]) / sum
						okPercentString = Number(okPercent * 100).toFixed(2) + "%"
					}
				});

				ctx.fillStyle = 'black';
				var fontSize = 40;
				var fontStyle = 'normal';
				var fontFamily = "Arial";
				ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);

				ctx.textAlign = 'center';
				ctx.textBaseline = 'middle';

				var centerX = ((chartInstance.chartArea.left + chartInstance.chartArea.right) / 2);
				var centerY = ((chartInstance.chartArea.top + chartInstance.chartArea.bottom) / 2);

				ctx.fillText(okPercentString, centerX, centerY);
			}
		}
	});

	var config = {
		type: 'doughnut',
		data: {
			labels: ['暫不需保養', '即將過期', '已過期'],
			datasets: [{
				data: defaultValue,
				backgroundColor: [
					"#00FF00",
					"#FFFF00",
					"#FF0000"
				],
				hoverBackgroundColor: [
					"#00FF00",
					"#FFFF00",
					"#FF0000"
				]
			}]
		},
		options: {
			legend: {
				labels: {
					fontSize: 20,
					fontFamily: '微軟正黑體'
				}
			},
			tooltips: {
				enabled: false
			}
		}
	};

	var ctx = document.getElementById("EMLineDetailDoughnut").getContext("2d");
	var myChart = new Chart(ctx, config);
}

