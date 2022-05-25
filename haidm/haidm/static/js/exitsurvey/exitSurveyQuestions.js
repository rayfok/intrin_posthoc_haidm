const defaultLikertScaleOptions = [
  "Strongly Disagree",
  "Somewhat Disagree",
  "Neutral",
  "Somewhat Agree",
  "Strongly Agree",
];

export const questions = {
  understandModel: {
    type: "likert",
    label: "I understand how the model makes predictions.",
    options: defaultLikertScaleOptions,
  },
  improveDecisionMaking: {
    type: "likert",
    label: "The model improved my decision-making.",
    options: defaultLikertScaleOptions,
  },
  modelUsage: {
    type: "shortAnswer",
    label:
      "Describe if and how you used the information that the model provided.",
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
