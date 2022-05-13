import Button from "@material-ui/core/Button";
import PropTypes from "prop-types";
import React, { Component } from "react";
import MUISelect from "./Select";
import ShortAnswer from "./ShortAnswer";

class ExitSurvey extends Component {
  static propTypes = {
    submitMTurk: PropTypes.func,
  };

  ageOptions = {
    "18-24": "18-24",
    "25-29": "25-29",
    "30-39": "30-39",
    "40-49": "40-49",
    "50-59": "50-59",
    "60-69": "60-69",
    "70-79": "70-79",
    "80 or above": "80 or above",
    "Prefer not to say": "Prefer not to say",
  };

  raceOptions = {
    White: "White",
    Asian: "Asian",
    "Native Hawaiian or Other Pacific Islander":
      "Native Hawaiian or Other Pacific Islander",
    "American Indian or Alaska Native": "American Indian or Alaska Native",
    "Black or African American": "Black or African American",
    "Prefer not to say": "Prefer not to say",
  };

  genderOptions = {
    Female: "Female",
    Male: "Male",
    "Transgender Female": "Transgender Female",
    "Transgender Male": "Transgender Male",
    "Not listed": "Not listed",
    "Prefer not to say": "Prefer not to say",
  };

  educationOptions = {
    "No high school diploma": "No high school diploma",
    "High school degree or equivalent": "High school degree or equivalent",
    "Associate degree": "Associate degree",
    "Bachelor’s degree": "Bachelor’s degree",
    "Master’s degree": "Master’s degree",
    Doctorate: "Doctorate",
    "Professional degree": "Professional degree",
    "Prefer not to say": "Prefer not to say",
  };

  constructor(props) {
    super(props);
    this.state = {
      age: "",
      race: "",
      gender: "",
      education: "",
      influenceDecisionMaking: "",
      influenceUnderstanding: "",
    };
  }

  updateAge = (age) => this.setState({ age });
  updateRace = (race) => this.setState({ race });
  updateGender = (gender) => this.setState({ gender });
  updateEducation = (education) => this.setState({ education });
  updateInfluenceDecisionMaking = (influenceDecisionMaking) =>
    this.setState({ influenceDecisionMaking });
  updateInfluenceUnderstanding = (influenceUnderstanding) =>
    this.setState({ influenceUnderstanding });

  render() {
    return (
      <div id="exit-survey-container">
        <p className="task-section-header">Demographic</p>
        <div className={"exit-survey-select"}>
          <MUISelect
            label="Age"
            callback={this.updateAge}
            options={this.ageOptions}
          />
        </div>
        <div className={"exit-survey-select"}>
          <MUISelect
            label="Race"
            callback={this.updateRace}
            options={this.raceOptions}
          />
        </div>
        <div className={"exit-survey-select"}>
          <MUISelect
            label="Gender Identity"
            callback={this.updateGender}
            options={this.genderOptions}
          />
        </div>
        <div className={"exit-survey-select"}>
          <MUISelect
            label="Highest education level achieved"
            callback={this.updateEducation}
            options={this.educationOptions}
          />
        </div>
        <div className={"exit-survey-short-ans"}>
          <ShortAnswer
            label="How did the AI's explanation influence your decision-making?"
            callback={this.updateInfluenceDecisionMaking}
          />
        </div>
        <div className={"exit-survey-short-ans"}>
          <ShortAnswer
            label="How did the AI's explanation influence your understanding of the model?"
            callback={this.updateInfluenceUnderstanding}
          />
        </div>
        <Button
          variant="contained"
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
