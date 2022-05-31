import Button from "@material-ui/core/Button";
import Tooltip from "@material-ui/core/Tooltip";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { questions } from "./exitSurveyQuestions";
import LikertScaleQuestion from "./LikertScaleQuestion";
import MultipleChoiceQuestion from "./MultipleChoiceQuestion";
import MultiSelectQuestion from "./MultiSelectQuestion";
import SelectQuestion from "./SelectQuestion";
import ShortAnswerQuestion from "./ShortAnswerQuestion";

class ExitSurvey extends Component {
  static propTypes = {
    task: PropTypes.string,
    saveExitSurveyResponses: PropTypes.func,
    onSubmit: PropTypes.func,
  };

  constructor(props) {
    super(props);
    this.state = {
      responses: {},
      questions: {},
    };
  }

  componentDidMount() {
    window.scrollTo(0, 0);
    this.setState({
      questions: Object.entries(questions)
        .filter(([_, q]) => !("task" in q) || q.task === this.props.task)
        .reduce((acc, [k, v]) => {
          acc[k] = v;
          return acc;
        }, {}),
    });
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
      .then(this.props.onSubmit);
  };

  isSurveyCompleted = () => {
    return (
      Object.keys(this.state.responses).length ===
      Object.keys(this.state.questions).length
    );
  };

  render() {
    return (
      <div id="exit-survey-container">
        <h4 style={{ textAlign: "center" }}>Exit Survey</h4>
        <p className="task-section-header">
          Please respond to all of the following questions.
        </p>
        {Object.entries(this.state.questions).map(([name, q]) => {
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
          } else if (q.type === "multipleChoice") {
            return (
              <div
                style={{
                  border: "1px solid black",
                  borderRadius: "5px",
                  padding: "10px",
                  marginBottom: "10px",
                }}
                key={name}
              >
                <MultipleChoiceQuestion
                  context={q.context}
                  prompt={q.prompt}
                  options={q.options}
                  callback={(v) => this.updateResponse(name, v)}
                  key={name}
                />
              </div>
            );
          } else if (q.type === "multiSelect") {
            return (
              <div
                style={{
                  border: "1px solid black",
                  borderRadius: "5px",
                  padding: "10px",
                  marginBottom: "10px",
                }}
                key={name}
              >
                <MultiSelectQuestion
                  context={q.context}
                  prompt={q.prompt}
                  options={q.options}
                  callback={(v) => this.updateResponse(name, v)}
                  key={name}
                />
              </div>
            );
          }
        })}

        <Tooltip
          title={
            !this.isSurveyCompleted() ? "Please respond to all questions." : ""
          }
          placement="bottom"
        >
          <div>
            <Button
              variant="contained"
              className="centered button"
              id="submit-button"
              onClick={this.submit}
              disabled={!this.isSurveyCompleted()}
            >
              Submit Responses
            </Button>
          </div>
        </Tooltip>
      </div>
    );
  }
}

export default ExitSurvey;
