const defaultLikertScaleOptions = [
  "Strongly Disagree",
  "Somewhat Disagree",
  "Neutral",
  "Somewhat Agree",
  "Strongly Agree",
];

export const questions = {
  recognizeIncorrect: {
    type: "likert",
    label: "I easily recognized when the model was likely to be incorrect.",
    options: defaultLikertScaleOptions,
  },
  recognizeCorrect: {
    type: "likert",
    label: "I easily recognized when the model was likely to be correct.",
    options: defaultLikertScaleOptions,
  },
  perceivedImpact: {
    type: "likert",
    label: "The model influenced my decisions.",
    options: defaultLikertScaleOptions,
  },
  perceivedAccuracy: {
    type: "select",
    label: "How many decisions do you believe you got correct during the task?",
    options: {
      "0-5": "0-5",
      "6-10": "6-10",
      "11-15": "11-15",
      "16 or more": "16 or more",
    },
  },
  perceivedModelUtility: {
    type: "likert",
    label: "My final decisions were primarily the result of.",
    options: [
      "Completely my capabilities",
      "Mostly my capabilities",
      "A combination of capabilities",
      "Mostly the model's capabilities",
      "Completely the model's capabilities",
    ],
  },
  perceviedPredictionUtility: {
    type: "likert",
    label: "The model prediction improved my decision-making",
    options: defaultLikertScaleOptions,
  },
  perceviedExplanationUtility: {
    type: "likert",
    label: "The model explanation improved my decision-making",
    options: defaultLikertScaleOptions,
  },
  influenceDecisionMaking: {
    type: "shortAnswer",
    label: "How did the AI's explanation influence your decision-making?",
  },
  influenceUnderstanding: {
    type: "shortAnswer",
    label:
      "How did the AI's explanation influence your understanding of the model?",
  },
  age: {
    type: "select",
    label: "Age",
    options: {
      "18-24": "18-24",
      "25-29": "25-29",
      "30-39": "30-39",
      "40-49": "40-49",
      "50-59": "50-59",
      "60-69": "60-69",
      "70-79": "70-79",
      "80 or above": "80 or above",
      "Prefer not to say": "Prefer not to say",
    },
  },
  race: {
    type: "select",
    label: "Race",
    options: {
      White: "White",
      Asian: "Asian",
      "Native Hawaiian or Other Pacific Islander":
        "Native Hawaiian or Other Pacific Islander",
      "American Indian or Alaska Native": "American Indian or Alaska Native",
      "Black or African American": "Black or African American",
      "Prefer not to say": "Prefer not to say",
    },
  },
  gender: {
    type: "select",
    label: "Gender Identity",
    options: {
      Female: "Female",
      Male: "Male",
      "Transgender Female": "Transgender female",
      "Transgender Male": "Transgender male",
      "Not listed": "Not listed",
      "Prefer not to say": "Prefer not to say",
    },
  },
  education: {
    type: "select",
    label: "Highest education level achieved",
    options: {
      "No high school diploma": "No high school diploma",
      "High school degree or equivalent": "High school degree or equivalent",
      "Associate degree": "Associate degree",
      "Bachelor’s degree": "Bachelor’s degree",
      "Master’s degree": "Master’s degree",
      Doctorate: "Doctorate",
      "Professional degree": "Professional degree",
      "Prefer not to say": "Prefer not to say",
    },
  },
};
