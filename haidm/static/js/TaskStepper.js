import * as React from "react";
import { Stepper } from "react-form-stepper";
import { TaskStep } from "./enums";

TaskStepper.defaultProps = {
  activeStep: TaskStep.TaskDescription,
};

export default function TaskStepper(props) {
  const steps = Object.keys(TaskStep).map((k) => ({
    label: k.replace(/([a-z])([A-Z])/g, "$1 $2"), // Split camel-cased step names
  }));
  return (
    <div id="task-stepper">
      <Stepper steps={steps} activeStep={props.activeStep} />
    </div>
  );
}
