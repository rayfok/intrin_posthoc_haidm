import Button from "@material-ui/core/Button";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { questions } from "./exitSurveyQuestions";
import LikertScaleQuestion from "./LikertScaleQuestion";
import SelectQuestion from "./SelectQuestion";
import ShortAnswerQuestion from "./ShortAnswerQuestion";

class ExitSurvey extends Component {
  static propTypes = {
    saveExitSurveyResponses: PropTypes.func,
    submitMTurk: PropTypes.func,
  };

  constructor(props) {
    super(props);
    this.state = {
      responses: {},
    };
  }

  updateResponse = (questionKey, value) => {
    this.setState((prevState) => ({
      responses: {
        ...prevState.responses,
        [questionKey]: value,
      },
    }));
  };

  submit = () => {
    this.props
      .saveExitSurveyResponses(this.state.responses)
      .then(this.props.submitMTurk);
  };

  render() {
    return (
      <div id="exit-survey-container">
        <h4 style={{ textAlign: "center" }}>Exit Survey</h4>
        <p className="task-section-header">
          Please respond to all of the following questions.
        </p>
        {Object.entries(questions).map(([name, q]) => {
          if (q.type === "select") {
            return (
              <SelectQuestion
                label={q.label}
                options={q.options}
                callback={(v) => this.updateResponse(name, v)}
                key={name}
              />
            );
          } else if (q.type === "likert") {
            return (
              <LikertScaleQuestion
                label={q.label}
                options={q.options}
                callback={(v) => this.updateResponse(name, v)}
                key={name}
              />
            );
          } else if (q.type === "shortAnswer") {
            return (
              <ShortAnswerQuestion
                label={q.label}
                callback={(v) => this.updateResponse(name, v)}
                key={name}
              />
            );
          }
        })}

        <Button
          variant="contained"
          className="centered button"
          id="submit-button"
          onClick={this.submit}
        >
          Submit HIT
        </Button>
      </div>
    );
  }
}

export default ExitSurvey;
