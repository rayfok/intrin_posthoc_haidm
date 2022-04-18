import Button from "@material-ui/core/Button";
import PropTypes from "prop-types";
import React, { Component } from "react";

class ExitSurvey extends Component {
  static propTypes = {
    submitMTurk: PropTypes.func,
  };

  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div id="exit-survey-container">
        <Button
          variant="contained"
          color="primary"
          className="centered button"
          onClick={this.props.submitMTurk}
        >
          Submit HIT
        </Button>
      </div>
    );
  }
}

export default ExitSurvey;
