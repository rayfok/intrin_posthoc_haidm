import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactApexChart from "react-apexcharts";

class LineChart extends Component {
  static propTypes = {
    data: PropTypes.array,
    title: PropTypes.string,
    currentValue: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  };

  constructor(props) {
    super(props);
  }

  render() {
    const { title, data, currentValue } = this.props;
    let currentValueOneHot = -1;
    if (title === "Sex") {
      currentValueOneHot = currentValue === "Male" ? 1 : 0;
    }
    if (title === "Charge Degree") {
      currentValueOneHot = currentValue === "Felony" ? 1 : 0;
    }

    const series = [
      {
        name: title,
        data: data,
      },
    ];
    const options = {
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
          series={series}
          type="line"
          width={440}
        />
      </div>
    );
  }
}

export default LineChart;
