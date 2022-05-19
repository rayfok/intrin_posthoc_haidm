import Button from "@material-ui/core/Button";
import InfoIcon from "@mui/icons-material/Info";
import Checkbox from "@mui/material/Checkbox";
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
import ExitSurvey from "./exitsurvey/ExitSurvey";
import ProgressIndicator from "./ProgressIndicator";
import TaskStepper from "./TaskStepper";
import DivergingBarChart from "./visualizations/DivergingBarChart";
import LineChart from "./visualizations/LineChart";

const APPLICATION_ROOT = "/haidm";

class MainTask extends Component {
  urlParams = new URLSearchParams(window.location.search);
  featureDisplayNameMap = {
    compas: {
      age: "Age",
      sex: "Sex",
      priors_count: "Prior Charges Count",
      c_charge_degree: "Charge Degree",
      c_charge_desc: "Charge Description",
      juv_fel_count: "Juvenile Felony Count",
      juv_misd_count: "Juvenile Misdemeanor Count",
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
  labelStringNames = {
    compas: {
      positive: "Will reoffend",
      negative: "Will not reoffend",
    },
    beer: {
      positive: "Positive",
      negative: "Negative",
    },
  };
  conditions = [
    "human",
    "human-ai",
    "human-ai-intrinsic",
    "human-ai-posthoc",
    "human-ai-intrinsic-global",
    "human-ai-gam",
  ];
  numberOfTrainingQuestions = 1;
  numberOfQuestions = 1;

  constructor(props) {
    super(props);
    this.state = {
      data: null,
      trainingQuestions: [],
      questions: [],
      responses: [],
      trainingCompletedCount: 0,
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
      activeStep: TaskStep.Instructions,
      acceptedTermsAndConds: false,
      showMachineAssistance: false,
    };
  }

  componentDidMount = async () => {
    let previouslyCompleted = await this.checkHasPreviouslyCompleted();
    if (!previouslyCompleted) {
      let data = await this.getData();
      const allQuestionsSorted = Object.values(data["instances"]).sort(
        (a, b) => parseInt(a.id) - parseInt(b.id)
      );
      let questions = allQuestionsSorted.slice(0, this.numberOfQuestions);
      let trainingQuestions = allQuestionsSorted.slice(
        this.numberOfQuestions,
        this.numberOfQuestions + this.numberOfTrainingQuestions
      );
      if (questions) {
        this.setState({
          data,
          trainingQuestions,
          questions,
          activeStep: TaskStep.Instructions,
        });
      }
    }
  };

  startOnboarding = () => {
    this.setState(
      {
        activeStep: TaskStep.TaskOnboarding,
      },
      this.setNextQuestion
    );
  };

  startMainTask = () => {
    this.setState(
      {
        activeStep: TaskStep.MainTask,
      },
      this.setNextQuestion
    );
  };

  getData = async () => {
    let url = `${APPLICATION_ROOT}/api/v1/q/?task=${this.state.task}&q=-1`;
    try {
      let response = await fetch(url, { credentials: "same-origin" });
      let data = await response.json();
      return data;
    } catch (err) {
      return [];
    }
  };

  setNextQuestion = () => {
    this.setState({
      curQuestion:
        this.state.activeStep === TaskStep.MainTask
          ? this.state.questions[this.state.completedCount]
          : this.state.trainingQuestions[this.state.trainingCompletedCount],
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
        ai_decision: this.state.curQuestion["preds"]["logr"],
        initial_decision_time: this.state.initialDecisionTime,
        final_decision_time: Date.now() - this.state.questionStartTime,
        ground_truth: this.state.curQuestion["label"],
      };
      if (this.state.activeStep === TaskStep.TaskOnboarding) {
        this.setState(
          (prevState) => ({
            trainingCompletedCount: prevState.trainingCompletedCount + 1,
          }),
          () => {
            if (
              this.state.trainingCompletedCount >=
              this.state.trainingQuestions.length
            ) {
              this.startMainTask();
            } else {
              this.setNextQuestion();
            }
          }
        );
      } else if (this.state.activeStep === TaskStep.MainTask) {
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
    }
  };

  submitData = async () => {
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
  };

  saveExitSurveyResponses = async (exitSurveyResponses) => {
    let url = `${APPLICATION_ROOT}/api/v1/submit-exit-survey/`;
    let response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify({
        responses: {
          ...exitSurveyResponses,
          worker_id: this.state.workerId,
          hit_id: this.state.hitId,
          assignment_id: this.state.assignmentId,
          task: this.state.task,
          condition: this.state.condition,
        },
      }),
    });
    return response["success"];
  };

  submitMTurk = () => {
    if (this.state.turkSubmitTo !== null) {
      const form = document.getElementById("final-submit-form");
      form.submit();
    } else {
      location.reload();
    }
  };

  checkHasPreviouslyCompleted = async () => {
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

  machineSuggestReoffend = () => {
    if (
      this.state.condition === "human-ai" ||
      this.state.condition === "human-ai-posthoc"
    ) {
      return this.state.curQuestion["preds"]["svm"] === 1;
    } else if (
      this.state.condition === "human-ai-intrinsic" ||
      this.state.condition === "human-ai-intrinsic-global"
    ) {
      return this.state.curQuestion["preds"]["logr"] === 1;
    } else if (this.state.condition === "human-ai-gam") {
      return this.state.curQuestion["preds"]["gam"] === 1;
    } else {
      return 0;
    }
  };

  getFeatureContributions = () => {
    const { condition, curQuestion, task } = this.state;
    let expl = null;

    if (condition === "human-ai-intrinsic") {
      expl = curQuestion["expls"]["logr_prob"];
    } else if (condition === "human-ai-posthoc") {
      expl = curQuestion["expls"]["svc_lime"];
    } else if (condition === "human-ai-intrinsic-global") {
      expl = curQuestion["expls"]["logr_params"];
    }
    return Object.entries(this.featureDisplayNameMap[task]).reduce(
      (a, [rawName, formattedName]) => {
        if (rawName in expl) {
          const featureValue = curQuestion["features"][rawName];
          a[`${formattedName} = ${featureValue}`] = expl[rawName];
        }
        return a;
      },
      {}
    );
  };

  getExplanationDescription = () => {
    if (this.state.task === "compas") {
      return (
        <p>
          Our model has been previously trained with many profiles of other
          defendants who are known to have reoffended or not. Our model has
          learned whether specific features of a defendant increase or decrease
          the chance for a reoffense.
          <br />
          <br />
          <span>
            Positive values (shown in{" "}
            <span style={{ color: "#1976D2" }}>blue</span>) indicate that a
            feature <b>increases</b> the chance that a defendant will reoffend.
            Negative values (shown in{" "}
            <span style={{ color: "#DC143C" }}>red</span>) indicate that a
            feature <b>decreases</b> the chance that a defendant will reoffend.{" "}
          </span>
          {this.state.condition === "human-ai-gam" && (
            <span>
              The purple dotted lines indicate feature values for the current
              defendant.
            </span>
          )}
        </p>
      );
    } else if (this.state.task === "beer") {
      return (
        <p>
          {/* Our model has been previously trained with many other beer reviews for
          which their sentiments are known. Words highlighted in{" "}
          <span style={{ color: "#1976D2" }}>blue</span> indicate the model
          believes those words contribute to a positive review. Words
          highlighted in <span style={{ color: "#DC143C" }}>red</span> indicate
          the model believes those words contribute to a negative review. The
          intensity of highlights indicate how strongly each word affects the
          model's decision. */}
          Our model has been previously trained with many other beer reviews for
          which their sentiments are known. Words with a positive{" "}
          <span style={{ color: "#1976D2" }}>blue</span> value indicate the
          model believes those words contribute to a positive review. Words with
          a negative <span style={{ color: "#DC143C" }}>red</span> value
          indicate the model believes those words contribute to a negative
          review. The model makes a decision by adding together values for every
          word in the review.
        </p>
      );
    }
  };

  getInstructions = () => {
    if (this.state.task === "compas") {
      return (
        <p>
          You are here to help{" "}
          <b>
            predict whether a defendant currently charged with a crime will
            reoffend within the next two years
          </b>
          .{" "}
          {this.state.condition !== "human" && (
            <span>
              You will be assisted by an AI model throughout the task.{" "}
            </span>
          )}
          You will first complete {this.numberOfTrainingQuestions} training
          questions to familiarize yourself with the interface and task
          requirements, and then complete an additional {this.numberOfQuestions}{" "}
          questions comprising the actual task.
          <br />
          <br />
          Disclaimer: Note that while your decisions will not directly influence
          the lives of any defendants, they may be used to improve AI models
          that support criminal justice professionals.
          <br />
          <br />
        </p>
      );
    } else if (this.state.task === "beer") {
      return (
        <p>
          You are here to help{" "}
          <b>predict whether a review of a beer is positive or negative</b>.{" "}
          {this.state.condition !== "human" && (
            <span>
              You will be assisted by an AI model throughout the task.{" "}
            </span>
          )}
          You will first complete {this.numberOfTrainingQuestions} training
          questions to familiarize yourself with the interface and task
          requirements, and then complete an additional {this.numberOfQuestions}{" "}
          questions for the actual task.
          <br />
          <br />
        </p>
      );
    }
  };

  getTermsAndConditions = () => {
    return (
      <p>
        Participation is voluntary, you are free to release the HIT at any time,
        and refusing to be in the study or stopping participation will involve
        no penalty or loss of benefits to which you are otherwise entitled. Any
        identifiable information, including your MTurk ID, will be treated as
        confidential by the research team and will be deleted when no longer
        needed for quality control. If you have concerns about any information
        you see, please contact the researchers directly. If you have questions
        about your rights as a research participant, or wish to obtain
        information, ask questions, or discuss any concerns about this study
        with someone other than the researchers, please contact the University
        of Washington Human Subjects Division at +1-206-543-0098.
      </p>
    );
  };

  getDecisionPrompt = () => {
    if (this.state.task === "compas") {
      return "Do you think this defendant will reoffend within two years?";
    } else if (this.state.task === "beer") {
      return "What do you think is the sentiment of this review?";
    }
  };

  getPositiveDecisionText = () => {
    if (this.state.task === "compas") {
      return (
        <span>
          Yes, I think they <b>will</b> reoffend.
        </span>
      );
    } else if (this.state.task === "beer") {
      return <span>Positive</span>;
    }
  };

  getNegativeDecisiontext = () => {
    if (this.state.task === "compas") {
      return (
        <span>
          No, I think they <b>will not</b> reoffend.
        </span>
      );
    } else if (this.state.task === "beer") {
      return <span>Negative</span>;
    }
  };

  getTaskDescription = () => {
    if (this.state.task === "compas") {
      return (
        <React.Fragment>
          Please review the following profile and <b>carefully consider</b>{" "}
          whether this defendant is likely to reoffend within the next two
          years.
        </React.Fragment>
      );
    } else if (this.state.task === "beer") {
      return (
        <React.Fragment>
          Please read the following review of a beer to determine whether you
          believe the review is more positive or negative.
        </React.Fragment>
      );
    }
  };

  getAIDecisionText = () => {
    if (this.state.task === "compas") {
      return (
        <React.Fragment>
          Our model predicts that this defendant{" "}
          <b>{this.machineSuggestReoffend() ? "will" : "will not"}</b> reoffend
          within two years.
        </React.Fragment>
      );
    } else if (this.state.task === "beer") {
      return (
        <React.Fragment>
          Our model believes this review is more likely{" "}
          <b>{this.machineSuggestReoffend() ? "positive" : "negative"}</b>.
        </React.Fragment>
      );
    }
  };

  getTextWithHighlights = () => {
    const topK = 10; // Max number of highlights to show per class (pos/neg)
    let tokens = [];
    let weights = [];
    if (this.state.condition === "human-ai-intrinsic") {
      tokens = this.state.curQuestion["expls"]["logr"]["tokens"];
      weights = this.state.curQuestion["expls"]["logr"]["weights"];
    } else if (this.state.condition === "human-ai-posthoc") {
      tokens = this.state.curQuestion["expls"]["opaque"]["tokens"];
      weights = this.state.curQuestion["expls"]["opaque"]["weights"];
    }

    // Min-max normalization to use weights for determining highlight opacity
    const maxWeight = Math.max(...weights);
    const minWeight = Math.min(...weights);
    const normalizedWeights = weights.map(
      (w) => (w - minWeight) / (maxWeight - minWeight)
    );

    // Colorize the top-k highlights for each class
    const sortedIndices = Array.from(Array(weights.length).keys()).sort(
      (a, b) => (weights[a] < weights[b] ? -1 : (weights[b] < weights[a]) | 0)
    );
    const pos = sortedIndices.slice(-topK).filter((i) => weights[i] > 0);
    const neg = sortedIndices.slice(0, topK).filter((i) => weights[i] < 0);
    let colorized = [];
    tokens.forEach((t, i) => {
      if (pos.includes(i)) {
        colorized.push(
          <span
            style={{
              textDecoration: "underline",
              textDecorationColor: `rgb(25, 118, 210, ${normalizedWeights[i]}`,
              textDecorationThickness: "2px",
            }}
            key={i}
          >
            {t}
          </span>
        );
        colorized.push(<span> </span>);
      } else if (neg.includes(i)) {
        colorized.push(
          <span
            style={{
              textDecoration: "underline",
              textDecorationColor: `rgb(220, 20, 60, ${normalizedWeights[i]})`,
              textDecorationThickness: "2px",
            }}
            key={i}
          >
            {t}
          </span>
        );
      } else {
        colorized.push(<span key={i}>{t}</span>);
      }
      colorized.push(<span key={`space-${i}`}> </span>);
    });
    return colorized;
  };

  getTextFeatureContributions = () => {
    const topK = 20; // Max number of highlights to show per class (pos/neg)
    let tokens = [];
    let weights = [];
    if (this.state.condition === "human-ai-intrinsic") {
      tokens = this.state.curQuestion["expls"]["logr"]["tokens"];
      weights = this.state.curQuestion["expls"]["logr"]["weights"];
    } else if (this.state.condition === "human-ai-posthoc") {
      tokens = this.state.curQuestion["expls"]["opaque"]["tokens"];
      weights = this.state.curQuestion["expls"]["opaque"]["weights"];
    }

    // Colorize the top-k / 2 highlights for each class
    // const sortedIndices = Array.from(Array(weights.length).keys()).sort(
    //   (a, b) => (weights[a] < weights[b] ? -1 : (weights[b] < weights[a]) | 0)
    // );
    // const pos = sortedIndices.slice(int(-topK / 2)).filter((i) => weights[i] > 0);
    // const neg = sortedIndices.slice(0, int(topK / 2)).filter((i) => weights[i] < 0);
    // const topIndicesByMagnitude = pos
    //   .concat(neg)
    //   .sort((a, b) => (Math.abs(weights[a]) > Math.abs(weights[b]) ? -1 : 1));

    // Colorize the top-k highlights by absolute magnitude
    const topIndicesByMagnitude = Array.from(Array(weights.length).keys())
      .sort((a, b) => (Math.abs(weights[a]) > Math.abs(weights[b]) ? -1 : 1))
      .slice(0, topK);

    // Sum up all other feature contributions into a single value
    const other = weights.reduce((sum, weight, i) => {
      if (!topIndicesByMagnitude.includes(i)) {
        return sum + weight;
      } else {
        return sum;
      }
    }, 0);

    const textFeatureContributions = {};
    for (const i of topIndicesByMagnitude) {
      textFeatureContributions[tokens[i]] = weights[i];
    }
    textFeatureContributions["Total contribution of other words"] = other;
    return textFeatureContributions;
  };

  render() {
    const {
      data,
      task,
      trainingQuestions,
      questions,
      curQuestion,
      curDecision,
      initialDecision,
      trainingCompletedCount,
      completedCount,
      showMachineAssistance,
      activeStep,
      condition,
      acceptedTermsAndConds,
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

        <div id="task-stepper">
          <TaskStepper activeStep={activeStep} />
          {activeStep === TaskStep.TaskOnboarding && (
            <ProgressIndicator
              completed={trainingCompletedCount}
              total={trainingQuestions.length}
            />
          )}
          {activeStep === TaskStep.MainTask && (
            <ProgressIndicator
              completed={completedCount}
              total={questions.length}
            />
          )}
        </div>

        {activeStep === TaskStep.Instructions && (
          <div id="hit-description">
            <h5>
              Please accept the HIT before starting the task, and make sure to
              complete the HIT before it expires in 60 minutes.
            </h5>

            <strong>Task Description</strong>
            {this.getInstructions()}

            <strong>Terms and Conditions</strong>
            {this.getTermsAndConditions()}

            <FormControlLabel
              control={<Checkbox />}
              onChange={(e) =>
                this.setState({ acceptedTermsAndConds: e.target.checked })
              }
              label="I have read the task description and agree to the above terms and conditions."
            />

            <Button
              variant="contained"
              className="centered button"
              disabled={!acceptedTermsAndConds}
              onClick={this.startOnboarding}
            >
              Start
            </Button>
          </div>
        )}

        {activeStep === TaskStep.ExitSurvey && (
          <ExitSurvey
            saveExitSurveyResponses={this.saveExitSurveyResponses}
            submitMTurk={this.submitMTurk}
          />
        )}

        {(activeStep === TaskStep.MainTask ||
          activeStep === TaskStep.TaskOnboarding) &&
          curQuestion && (
            <div id="main-task-container">
              {activeStep === TaskStep.TaskOnboarding && (
                <h4 style={{ textAlign: "center" }}>PRACTICE</h4>
              )}

              <div id="task-description-container">
                <span id="task-description">{this.getTaskDescription()}</span>
              </div>

              {this.state.task === "compas" && (
                <div id="task-features-container">
                  <p className="task-section-header">Defendant Profile</p>
                  <TableContainer>
                    <Table id="task-features-table" size="small">
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
              )}
              {this.state.task === "beer" && (
                <div id="task-features-container">
                  <p className="task-section-header">Beer Review</p>
                  <span>
                    {curQuestion["expls"]["logr"]["tokens"].join(" ")}
                  </span>
                </div>
              )}

              <div id="task-choices-container">
                <p className="task-section-header">Make A Decision</p>
                <p
                  className={classNames("prompt-text", {
                    "text-muted": initialDecision !== null,
                  })}
                >
                  {this.getDecisionPrompt()}
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
                      label={this.getPositiveDecisionText()}
                    />
                    <FormControlLabel
                      value="no"
                      control={<Radio />}
                      disabled={initialDecision !== null}
                      label={this.getNegativeDecisiontext()}
                    />
                  </RadioGroup>
                </FormControl>
              </div>

              {showMachineAssistance && (
                <div id="ai-assist-container">
                  <div id="ai-decision">
                    <p className="task-section-header">AI Prediction</p>
                    <p>{this.getAIDecisionText()}</p>
                  </div>
                  {condition !== "human-ai" && (
                    <div id="ai-explanation">
                      <p className="task-section-header">
                        Here's how the model made its prediction
                      </p>
                      {this.getExplanationDescription()}

                      {this.state.task === "compas" &&
                        condition === "human-ai-gam" && (
                          <div id="gam-visualization">
                            {Object.keys(data["explanations"]["gam_pdp"]).map(
                              (feature) => (
                                <LineChart
                                  key={feature}
                                  splitColorOnSign={true}
                                  data={
                                    data["explanations"]["gam_pdp"][feature]
                                  }
                                  title={
                                    this.featureDisplayNameMap[task][feature]
                                  }
                                  currentValue={
                                    curQuestion["features"][feature]
                                  }
                                />
                              )
                            )}
                          </div>
                        )}
                      {this.state.task === "compas" &&
                        condition !== "human-ai-gam" && (
                          <DivergingBarChart
                            data={this.getFeatureContributions()}
                            positiveLabel={
                              this.labelStringNames[task]["positive"]
                            }
                            negativeLabel={
                              this.labelStringNames[task]["negative"]
                            }
                            title={`AI Prediction: ${
                              this.labelStringNames[task][
                                this.machineSuggestReoffend()
                                  ? "positive"
                                  : "negative"
                              ]
                            }`}
                          />
                        )}
                      {/* {this.state.task === "beer" && (
                        <div>{this.getTextWithHighlights()}</div>
                      )} */}
                      {this.state.task === "beer" && (
                        <DivergingBarChart
                          data={this.getTextFeatureContributions()}
                          positiveLabel={
                            this.labelStringNames[task]["positive"]
                          }
                          negativeLabel={
                            this.labelStringNames[task]["negative"]
                          }
                        />
                      )}
                    </div>
                  )}
                  <p className="task-section-header" id="final-decision-prompt">
                    Make Your Final Decision
                  </p>
                  <p className="prompt-text">{this.getDecisionPrompt()}</p>
                  <FormControl className="choices">
                    <RadioGroup
                      row
                      value={curDecision}
                      onChange={this.handleChoiceSelected}
                    >
                      <FormControlLabel
                        value="yes"
                        control={<Radio />}
                        label={this.getPositiveDecisionText()}
                      />
                      <FormControlLabel
                        value="no"
                        control={<Radio />}
                        label={this.getNegativeDecisiontext()}
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
                  {(() => {
                    if (activeStep === TaskStep.TaskOnboarding) {
                      if (
                        (this.state.initialDecision === null &&
                          this.state.condition !== "human") ||
                        trainingCompletedCount < trainingQuestions.length - 1
                      ) {
                        return "Next";
                      } else {
                        return "Start Main Task";
                      }
                    } else if (activeStep === TaskStep.MainTask) {
                      if (
                        (this.state.initialDecision === null &&
                          this.state.condition !== "human") ||
                        completedCount < questions.length - 1
                      ) {
                        return "Next";
                      } else {
                        return "Finish Main Task";
                      }
                    }
                  })()}
                </Button>
              </div>
            </div>
          )}
      </React.Fragment>
    );
  }
}

export default MainTask;
