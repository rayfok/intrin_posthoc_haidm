import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactApexChart from "react-apexcharts";

class DivergingBarChart extends Component {
  static propTypes = {
    data: PropTypes.object,
    positiveLabel: PropTypes.string,
    negativeLabel: PropTypes.string,
    title: PropTypes.string,
  };

  constructor(props) {
    super(props);
  }

  render() {
    const positive = Object.values(this.props.data).map((x) => (x < 0 ? 0 : x));
    const negative = Object.values(this.props.data).map((x) => (x > 0 ? 0 : x));
    const bound = Math.ceil(
      Math.max(...Object.values(this.props.data).map((x) => Math.abs(x)))
    );
    const series = [
      {
        name: this.props.positiveLabel,
        data: positive,
      },
      {
        name: this.props.negativeLabel,
        data: negative,
      },
    ];
    const options = {
      chart: {
        type: "bar",
        height: 440,
        stacked: true,
        toolbar: {
          show: false,
        },
      },
      colors: ["#008FFB", "#FF4560"],
      plotOptions: {
        bar: {
          horizontal: true,
          barHeight: "80%",
        },
      },
      dataLabels: {
        enabled: false,
      },
      stroke: {
        width: 1,
        colors: ["#fff"],
      },
      grid: {
        xaxis: {
          lines: {
            show: false,
          },
        },
      },
      yaxis: {
        labels: {
          maxWidth: 400,
          style: {
            fontSize: "14px",
          },
        },
      },
      xaxis: {
        min: -bound,
        max: bound,
        forceNiceScale: true,
        categories: Object.keys(this.props.data),
        title: {
          text: "Chance",
        },
        tickAmount: Math.max(2 * bound, 5),
      },
      title: {
        text: this.props.title,
        align: "center",
      },
    };

    return (
      <div id="diverging-bar-charts-container">
        <ReactApexChart
          options={options}
          series={series}
          type="bar"
          height={440}
        />
      </div>
    );
  }
}

export default DivergingBarChart;
