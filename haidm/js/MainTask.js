import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import React, { Component } from "react";
import FinishModal from "./FinishModal";

const APPLICATION_ROOT = "";

class MainTask extends Component {
  urlParams = new URLSearchParams(window.location.search);
  featureDisplayNameMap = {
    compas: {
      age: "Age",
      c_charge_degree: "Charge Degree",
      juv_fel_count: "Juvenile Felony Count",
      juv_misd_count: "Juvenile Misdemeanor Count",
      priors_count: "Prior Charges Count",
      sex: "Sex",
    },
  };

  constructor(props) {
    super(props);
    this.state = {
      questions: null,
      responses: [],
      completedCount: 0,
      workerId: this.urlParams.get("workerId"),
      assignmentId: this.urlParams.get("assignmentId"),
      hitId: this.urlParams.get("hitId"),
      turkSubmitTo: this.urlParams.get("turkSubmitTo"),
      task: this.urlParams.get("task"),
      condition: this.urlParams.get("condition"),
      questionStartTime: -1,
      initialDecisionTime: -1,
      initialDecision: null,
      curDecision: null,
      curQuestion: null,
      showMainTask: false,
      finished: false,
      previouslyCompleted: false,
    };
  }

  componentDidMount() {
    this.checkHasPreviouslyCompleted();
    this.getAllQuestions();
  }

  getAllQuestions = () => {
    let url = `${APPLICATION_ROOT}/api/v1/q/?task=${this.state.task}&q=-1`;
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Something went wrong getting all questions...");
        }
      })
      .then((data) => {
        this.setState(
          {
            questions: Object.values(data).sort(
              (a, b) => parseInt(a.id) - parseInt(b.id)
            ),
          },
          this.startTask
        );
      });
  };

  startTask = () => {
    this.setState(
      {
        showMainTask: true,
      },
      this.setNextQuestion
    );
  };

  setNextQuestion = () => {
    this.setState({
      curQuestion: this.state.questions[this.state.completedCount],
      questionStartTime: Date.now(),
      curDecision: null,
    });
  };

  handleChoiceSelected = (e) => {
    this.setState((prevState) => ({
      curDecision: e.target.value,
      initialDecision:
        initialDecision === null ? e.target.value : prevState.initialDecision,
      initialDecisionTime:
        initialDecisionTime === -1 ? Date.now() : prevState.initialDecisionTime,
    }));
  };

  saveResponse = () => {
    const response = {
      worker_id: this.state.workerId,
      hit_id: this.state.hitId,
      assisgnment_id: this.state.assignmentId,
      task: this.state.task,
      condition: this.state.condition,
      question_id: this.state.curQuestion["id"],
      initial_human_decision: this.state.initialDecision,
      final_human_decision: this.state.curDecision,
      initial_decision_time: this.state.initialDecisionTime,
      final_decision_time: Date.now() - this.state.questionStartTime,
    };
    this.setState(
      (prevState) => ({
        completedCount: prevState.completedCount + 1,
        responses: [...prevState.responses, response],
      }),
      () => {
        if (this.state.completedCount >= this.state.questions.length) {
          this.submitData();
          this.setState({ finished: true });
        }
      }
    );
  };

  submitData = () => {
    let url = `${APPLICATION_ROOT}/api/v1/submit/`;
    fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify({
        responses: this.state.responses,
      }),
    }).then(this.setState({ showMainTask: false, finished: true }));
  };

  submitMTurk = () => {
    if (this.state.turkSubmitTo !== null) {
      const form = document.getElementById("final-submit-form");
      form.submit();
    } else {
      location.reload();
    }
  };

  checkHasPreviouslyCompleted = () => {
    if (this.state.workerId !== null) {
      let url = `${APPLICATION_ROOT}/api/v1/completed/?workerId=${this.state.workerId}&task=${this.state.task}`;
      fetch(url, {
        method: "GET",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        credentials: "same-origin",
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error("Something went wrong ...");
          }
        })
        .then((data) => {
          this.setState({
            previouslyCompleted: data["completed"],
          });
        });
    }
  };

  getMTurkSubmitForm = () => {
    return (
      <form
        id="final-submit-form"
        action={this.state.turkSubmitTo + "/mturk/externalSubmit"}
        method="POST"
      >
        <input
          type="hidden"
          name="assignmentId"
          value={this.state.assignmentId || ""}
        />
        <input type="hidden" name="nonce" value={"ray" + Math.random()} />
      </form>
    );
  };

  render() {
    const {
      questions,
      curQuestion,
      curDecision,
      showMainTask,
      completedCount,
      finished,
    } = this.state;

    if (!questions) {
      return (
        <div>If this page does not load, please return the HIT. Sorry!</div>
      );
    }

    return (
      <div id="question-outer">
        <React.Fragment>
          {this.getMTurkSubmitForm()}

          <FinishModal submitMTurk={this.submitMTurk} open={finished} />

          {curQuestion && showMainTask && (
            <Grid container justifyContent="center" alignItems="center">
              <Grid item>
                <Paper id="question-inner">
                  <div id="features">
                    {Object.entries(curQuestion["features"])
                      .filter(([k, _]) =>
                        this.featureDisplayNameMap["compas"].hasOwnProperty(k)
                      )
                      .map(([k, v]) => (
                        <li key={k}>
                          {this.featureDisplayNameMap["compas"][k]}: {v}
                        </li>
                      ))}
                  </div>
                  <div id="choices"></div>
                  <div id="buttons">
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={this.saveResponse}
                      className="button"
                      disabled={curDecision === null}
                    >
                      {completedCount === questions.length - 1
                        ? "Submit"
                        : "Next"}
                    </Button>
                  </div>
                </Paper>
              </Grid>
            </Grid>
          )}
        </React.Fragment>
      </div>
    );
  }
}

export default MainTask;
