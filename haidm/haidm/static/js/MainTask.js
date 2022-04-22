import Button from "@material-ui/core/Button";
import InfoIcon from "@mui/icons-material/Info";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Tooltip from "@mui/material/Tooltip";
import classNames from "classnames";
import React, { Component } from "react";
import { TaskStep } from "./enums";
import ExitSurvey from "./ExitSurvey";
import ProgressIndicator from "./ProgressIndicator";
import TaskStepper from "./TaskStepper";

const APPLICATION_ROOT = "";

class MainTask extends Component {
  urlParams = new URLSearchParams(window.location.search);
  featureDisplayNameMap = {
    compas: {
      age: "Age",
      sex: "Sex",
      c_charge_degree: "Charge Degree",
      c_charge_desc: "Charge Description",
      juv_fel_count: "Juvenile Felony Count",
      juv_misd_count: "Juvenile Misdemeanor Count",
      priors_count: "Prior Charges Count",
    },
  };
  featureDescMap = {
    compas: {
      age: "Age of the defendant.",
      sex: "Biological sex designated at birth.",
      c_charge_degree:
        "Severity of the charged crime. Crimes are classified as either misdemeanors (less serious crimes) or felonies (more serious crimes)",
      c_charge_desc: "Description of the charged crime.",
      juv_fel_count:
        "Number of felony crimes commited while the defendant was a juvenile (under the age of eighteen).",
      juv_misd_count:
        "Number of misdemeanor crimes commited while the defendant was a juvenile (under the age of eighteen).",
      priors_count: "Total number of prior charges against the defendant.",
    },
  };
  conditions = ["human", "human-ai", "human-ai-intrinsic", "human-ai-posthoc"];
  numberOfQuestions = 5;

  constructor(props) {
    super(props);
    this.state = {
      questions: [],
      responses: [],
      completedCount: 0,
      workerId: this.urlParams.get("workerId"),
      assignmentId: this.urlParams.get("assignmentId"),
      hitId: this.urlParams.get("hitId"),
      turkSubmitTo: this.urlParams.get("turkSubmitTo"),
      task: this.urlParams.get("task"),
      condition: this.urlParams.get("condition") || "human-ai",
      questionStartTime: -1,
      initialDecisionTime: -1,
      finalDecisionTime: -1,
      initialDecision: null,
      finalDecision: null,
      curDecision: null,
      curQuestion: null,
      activeStep: TaskStep.TaskDescription,
    };
  }

  async componentDidMount() {
    let previouslyCompleted = await this.checkHasPreviouslyCompleted();
    if (!previouslyCompleted) {
      let questions = await this.getAllQuestions();
      if (questions) {
        this.setState({
          questions,
          activeStep: TaskStep.TaskDescription,
        });
      }
    }
  }

  startOnboarding = () => {
    this.setState({
      activeStep: TaskStep.TaskOnboarding,
    });
  };

  startMainTask = () => {
    this.setState(
      {
        activeStep: TaskStep.MainTask,
      },
      this.setNextQuestion
    );
  };

  async getAllQuestions() {
    let url = `${APPLICATION_ROOT}/api/v1/q/?task=${this.state.task}&q=-1`;
    try {
      let response = await fetch(url, { credentials: "same-origin" });
      let data = await response.json();
      let questions = Object.values(data)
        .sort((a, b) => parseInt(a.id) - parseInt(b.id))
        .slice(0, this.numberOfQuestions);
      return questions;
    } catch (err) {
      return [];
    }
  }

  setNextQuestion = () => {
    this.setState({
      curQuestion: this.state.questions[this.state.completedCount],
      questionStartTime: Date.now(),
      curDecision: null,
      initialDecision: null,
      initialDecisionTime: -1,
      finalDecision: null,
      finalDecisionTime: -1,
      showMachineAssistance: false,
    });
  };

  handleChoiceSelected = (e) => {
    this.setState({
      curDecision: e.target.value,
    });
  };

  handleNextClicked = () => {
    if (
      this.state.initialDecision === null &&
      this.state.condition !== "human"
    ) {
      this.setState({
        showMachineAssistance: true,
        initialDecision: this.state.curDecision,
        initialDecisionTime: Date.now() - this.state.questionStartTime,
        curDecision: null,
      });
    } else {
      const response = {
        worker_id: this.state.workerId,
        hit_id: this.state.hitId,
        assignment_id: this.state.assignmentId,
        task: this.state.task,
        condition: this.state.condition,
        question_id: this.state.curQuestion["id"],
        initial_human_decision: this.state.initialDecision,
        final_human_decision: this.state.curDecision,
        ai_decision: this.state.curQuestion["preds"]["lgr"],
        initial_decision_time: this.state.initialDecisionTime,
        final_decision_time: Date.now() - this.state.questionStartTime,
        ground_truth: this.state.curQuestion["label"],
      };
      this.setState(
        (prevState) => ({
          completedCount: prevState.completedCount + 1,
          responses: [...prevState.responses, response],
        }),
        () => {
          if (this.state.completedCount >= this.state.questions.length) {
            this.submitData().then(() =>
              this.setState({
                activeStep: TaskStep.ExitSurvey,
              })
            );
          } else {
            this.setNextQuestion();
          }
        }
      );
    }
  };

  async submitData() {
    let url = `${APPLICATION_ROOT}/api/v1/submit/`;
    let response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify({
        responses: this.state.responses,
      }),
    });
    return response["success"];
  }

  submitMTurk = () => {
    if (this.state.turkSubmitTo !== null) {
      const form = document.getElementById("final-submit-form");
      form.submit();
    } else {
      location.reload();
    }
  };

  async checkHasPreviouslyCompleted() {
    if (this.state.workerId === null) return false;

    let url = `${APPLICATION_ROOT}/api/v1/completed/?workerId=${this.state.workerId}&task=${this.state.task}`;
    let response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
    });
    let data = await response.json();
    return data["completed"];
  }

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

  machineSuggestReoffend = () => {
    if (
      this.state.condition === "human-ai" ||
      this.state.condition === "human-ai-posthoc"
    ) {
      return this.state.curQuestion["preds"]["svc"] === 1;
    } else if (this.state.condition === "human-ai-intrinsic") {
      return this.state.curQuestion["preds"]["lgr"] === 1;
    } else {
      return 0;
    }
  };

  render() {
    const {
      task,
      questions,
      curQuestion,
      curDecision,
      initialDecision,
      completedCount,
      showMachineAssistance,
      activeStep,
    } = this.state;

    if (questions.length === 0) {
      return (
        <div id="return-hit-message">
          <p>
            If this message does not go away in a few seconds, either something
            has gone catastrophically wrong or our records indicate that you
            have already previously completed our task. Please do not accept
            this HIT, or return if already accepted. Thank you!
          </p>
        </div>
      );
    }

    return (
      <React.Fragment>
        {this.getMTurkSubmitForm()}

        <TaskStepper activeStep={activeStep} />

        {activeStep === TaskStep.TaskDescription && (
          <div id="hit-description">
            <p>Here goes the description of the task.</p>
            <Button
              variant="contained"
              className="centered button"
              onClick={this.startOnboarding}
            >
              Start
            </Button>
          </div>
        )}

        {activeStep === TaskStep.TaskOnboarding && (
          <div id="onboarding">
            <p>Here go the tutorial/gating questions.</p>
            <Button
              variant="contained"
              className="centered button"
              onClick={this.startMainTask}
            >
              Start
            </Button>
          </div>
        )}

        {activeStep === TaskStep.ExitSurvey && (
          <ExitSurvey submitMTurk={this.submitMTurk} />
        )}

        {activeStep === TaskStep.MainTask && curQuestion && (
          <div id="main-task-container">
            <ProgressIndicator
              value={(completedCount / questions.length) * 100}
            />

            <div id="task-description-container">
              <span id="task-description">
                Please review the following profile and consider whether this
                defendant is likely to reoffend within the next two years.
              </span>
            </div>

            <div id="task-features-container">
              <p className="task-section-header">Defendant Profile</p>
              <TableContainer>
                <Table sx={{ maxWidth: 500 }} size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>{<b>Feature</b>}</TableCell>
                      <TableCell align="right">{<b>Value</b>}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(curQuestion["features"])
                      .filter(([k, _]) =>
                        this.featureDisplayNameMap[task].hasOwnProperty(k)
                      )
                      .map(([k, v]) => (
                        <TableRow key={k}>
                          <TableCell component="th" scope="row">
                            {this.featureDisplayNameMap[task][k]}
                            <Tooltip title={this.featureDescMap[task][k]}>
                              <IconButton>
                                <InfoIcon sx={{ fontSize: 18 }} />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                          <TableCell align="right">{v}</TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </div>

            <div id="task-choices-container">
              <p className="task-section-header">Make A Decision</p>
              <p
                className={classNames("prompt-text", {
                  "text-muted": initialDecision !== null,
                })}
              >
                Do you think this defendant will reoffend within two years?
              </p>
              <FormControl className="choices">
                <RadioGroup
                  row
                  value={initialDecision ? initialDecision : curDecision}
                  onChange={this.handleChoiceSelected}
                >
                  <FormControlLabel
                    value="yes"
                    control={<Radio />}
                    disabled={initialDecision !== null}
                    label={
                      <span>
                        Yes, I think they <b>will</b> reoffend.
                      </span>
                    }
                  />
                  <FormControlLabel
                    value="no"
                    control={<Radio />}
                    disabled={initialDecision !== null}
                    label={
                      <span>
                        No, I think they <b>will not</b> reoffend.
                      </span>
                    }
                  />
                </RadioGroup>
              </FormControl>
            </div>

            {showMachineAssistance && (
              <div id="ai-assist-container">
                <div id="ai-decision">
                  <p className="task-section-header">AI Prediction</p>
                  <p>
                    Our AI model predicts that this defendent{" "}
                    <b>{this.machineSuggestReoffend() ? "will" : "will not"}</b>{" "}
                    reoffend within two years.
                  </p>
                </div>
                <div id="ai-explanation"></div>
                <p className="task-section-header">Make Your Final Decision</p>
                <p className="prompt-text">
                  Now, do you think this defendant will reoffend within two
                  years?
                </p>
                <FormControl className="choices">
                  <RadioGroup
                    row
                    value={curDecision}
                    onChange={this.handleChoiceSelected}
                  >
                    <FormControlLabel
                      value="yes"
                      control={<Radio />}
                      label={
                        <span>
                          Yes, I think they <b>will</b> reoffend.
                        </span>
                      }
                    />
                    <FormControlLabel
                      value="no"
                      control={<Radio />}
                      label={
                        <span>
                          No, I think they <b>will not</b> reoffend.
                        </span>
                      }
                    />
                  </RadioGroup>
                </FormControl>
              </div>
            )}

            <div id="task-buttons-container">
              <Button
                variant="contained"
                className="centered button"
                onClick={this.handleNextClicked}
                disabled={curDecision === null}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </React.Fragment>
    );
  }
}

export default MainTask;
