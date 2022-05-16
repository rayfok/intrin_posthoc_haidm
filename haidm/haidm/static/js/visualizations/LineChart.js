import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactApexChart from "react-apexcharts";

class LineChart extends Component {
  static propTypes = {
    data: PropTypes.array,
    title: PropTypes.string,
    currentValue: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    splitColorOnSign: PropTypes.bool,
  };

  constructor(props) {
    super(props);
  }

  red = "#DC143C";
  blue = "#1976D2";

  getSignSplitSeries = () => {
    let colors = [];
    let signSplitData = [];
    let curSign = "positive";
    let curData = [];
    for (const [x, y] of this.props.data) {
      if (curSign === "positive") {
        if (y > 0) {
          curData.push([x, y]);
        } else {
          if (curData.length > 0) {
            signSplitData.push(curData);
            colors.push(this.blue);
          }
          curSign = "negative";
          curData = [[x, y]];
        }
      } else {
        if (y <= 0) {
          curData.push([x, y]);
        } else {
          if (curData.length > 0) {
            signSplitData.push(curData);
            colors.push(this.red);
          }
          curSign = "positive";
          curData = [[x, y]];
        }
      }
    }
    if (curData.length > 0) {
      signSplitData.push(curData);
      colors.push(curSign === "positive" ? this.blue : this.red);
    }
    const series = signSplitData.map((d) => ({
      data: d,
    }));
    return [series, colors];
  };

  render() {
    const { title, data, currentValue, splitColorOnSign } = this.props;
    let currentValueOneHot = -1;
    if (title === "Sex") {
      currentValueOneHot = currentValue === "Male" ? 1 : 0;
    }
    if (title === "Charge Degree") {
      currentValueOneHot = currentValue === "Felony" ? 1 : 0;
    }

    const [signSplitSeries, colors] = this.getSignSplitSeries();

    const series = [
      {
        name: title,
        data: data,
      },
    ];
    const options = {
      colors: splitColorOnSign ? colors : [this.blue],
      annotations: {
        xaxis: [
          {
            x:
              title === "Sex" || title === "Charge Degree"
                ? currentValueOneHot
                : currentValue,
            borderColor: "#775DD0",
          },
        ],
      },
      chart: {
        type: "line",
        width: 440,
        toolbar: {
          show: false,
        },
        animations: {
          enabled: false,
        },
      },
      dataLabels: {
        enabled: false,
      },
      stroke: {
        width: 3,
      },
      xaxis: {
        type: "numeric",
        labels: {
          formatter: (value) => {
            if (title === "Sex") {
              if (value === 0) return "Female";
              else return "Male";
            }
            if (title === "Charge Degree") {
              if (value === 0) return "Misdemeanor";
              else return "Felony";
            }
            return Math.round(value);
          },
        },
      },
      legend: {
        show: false,
      },
      tooltip: {
        enabled: false,
      },
      yaxis: {
        labels: {
          formatter: (value) => {
            return +value.toFixed(2);
          },
        },
      },
      title: {
        text: `${this.props.title} = ${currentValue}`,
        align: "center",
      },
    };

    return (
      <div className="line-chart-container">
        <ReactApexChart
          options={options}
          series={splitColorOnSign ? signSplitSeries : series}
          type="line"
          width={440}
        />
      </div>
    );
  }
}

export default LineChart;
