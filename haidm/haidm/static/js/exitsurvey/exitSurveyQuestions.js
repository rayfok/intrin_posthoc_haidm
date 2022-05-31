const defaultLikertScaleOptions = [
  "Strongly Disagree",
  "Somewhat Disagree",
  "Neutral",
  "Somewhat Agree",
  "Strongly Agree",
];

export const questions = {
  compas1: {
    task: "compas",
    type: "multipleChoice",
    context:
      "Consider the following defendant:<br/><br/> A 25-year old female charged with a felony crime for Possession of Oxycodone, with no prior charges, no prior juvenile felony charges, and no prior juvenile misdemeanor charges.",
    prompt:
      "When all other features are kept the same, if the defendant’s age were 35 instead of 25, how would the model’s prediction on the defendant’s likelihood of reoffending change?",
    options: {
      "More likely reoffend":
        "The model would predict a 35-year old defendant to be <b>more</b> likely to reoffend.",
      "Less likely reoffend":
        "The model would predict a 35-year old defendant to be <b>less</b> likely to reoffend.",
    },
  },
  compas2: {
    task: "compas",
    type: "multipleChoice",
    context:
      "Consider the following defendant:<br/><br/> A 34-year old male charged with a felony crime for Felony Battery w/Prior Convict, with 4 prior charges, 2 prior juvenile felony charges, and no prior juvenile misdemeanor charges.",
    prompt:
      "When all other features are kept the same, if the defendant had 2 prior charges instead of 4, how would the model’s prediction on the defendant’s likelihood of reoffending change?",
    options: {
      "More likely reoffend":
        "The model would predict a defendant with 2 prior charges instead of 4 to be <b>more</b> likely to reoffend.",
      "Less likely reoffend":
        "The model would predict a defendant with 2 prior charges instead of 4 to be <b>less</b> likely to reoffend.",
    },
  },
  compas3: {
    task: "compas",
    type: "multipleChoice",
    context:
      "Consider the following defendant:<br/><br/> A 34-year old male charged with a misdemeanor crime for DUI Level 0.15 Or Minor In Veh, with 1 prior charge, no prior juvenile felony charges, and no prior juvenile misdemeanor charges.",
    prompt:
      "When all other features are kept the same, if the defendant were instead charged with a felony crime, how would the model’s prediction on the defendant’s likelihood of reoffending change?",
    options: {
      "More likely reoffend":
        "The model would predict a defendant charged with a felony to be <b>more</b> likely to reoffend.",
      "Less likely reoffend":
        "The model would predict a defendant charged with a felony to be <b>less</b> likely to reoffend.",
    },
  },
  beer1: {
    task: "beer",
    type: "multipleChoice",
    context:
      "Consider the following review: <br/><br/> Bottle, courtesy of fonefan. A clear, golden beer topped by a small, dense, off-white head leaving some curtains. <b>Fruity on the nose, slighlty syrupy, with white sugar.</b> Weak. The flavor is fruity, with white sugar, grass and hints of spices. Some bitterness in the end. Medium body, effervescent. A rather boring and anonymous witbier. 091025",
    prompt:
      "When the rest of the review is kept the same, if the bolded sentence were removed, how would the model's prediction on the review's likelihood of being positive change?",
    options: {
      "More likely positive":
        "The model would predict the review to be <b>more</b> likely to be positive.",
      "Less likely positive":
        "The model would predict the review to be <b>less</b> likely to be positive.",
    },
  },
  beer2: {
    task: "beer",
    type: "multipleChoice",
    context:
      "Consider the following review: <br/><br/> <b>12h April 2011Bottle from Bier Koning.</b> Cloudy amber beer, small white head. Softish dry palate. Dry malt - trace of soap. A whisper of citrus. Dry minerally finish. Too dry!",
    prompt:
      "When the rest of the review is kept the same, if the bolded sentence were removed, how would the model's prediction on the review's likelihood of being positive change?",
    options: {
      "More likely positive":
        "The model would predict the review to be <b>more</b> likely to be positive.",
      "Less likely positive":
        "The model would predict the review to be <b>less</b> likely to be positive.",
    },
  },
  beer3: {
    task: "beer",
    type: "multiSelect",
    context:
      "Consider the following review: <br/><br/> Bottle 330ml @ fonefan. Pours clear amber with a off-white head. Aroma has notes of wheat and fruity hops. Taste is light to medium sweet. Body is medium, texture is thin, carbonation is soft.",
    prompt:
      "The model currently predicts that this review is positive. Which of the following sentences if removed would <b>increase</b> the model's prediction on the review's likelihood of being <b>positive</b>? Please check all that apply.",
    options: {
      "Sentence 1": "Remove the sentence: Bottle 330ml @ fonefan",
      "Sentence 2":
        "Remove the sentence: Pours clear amber with a off-white head.",
      "Sentence 3":
        "Remove the sentence: Aroma has notes of wheat and fruity hops.",
      "Sentence 4": "Remove the sentence: Taste is light to medium sweet.",
      "Sentence 5":
        "Remove the sentence: Body is medium, texture is thin, carbonation is soft.",
      "None of the above": "None of the above",
    },
  },
  beer4: {
    task: "beer",
    type: "multiSelect",
    context:
      "Consider the following review: <br/><br/> Some lactose-sweetness in the aroma, with roasted malts. Very non-complex and typical for the average Impy Stout. Pretty thin and not very smooth. Lots of caramel and cocoa in the flavor. The alcohol is pretty obvious.",
    prompt:
      "The model currently predicts that this review is positive. Which of the following sentences if removed would <b>increase</b> the model's prediction on the review's likelihood of being <b>positive</b>? Please check all that apply.",
    options: {
      "Sentence 1":
        "Remove the sentence: Some lactose-sweetness in the aroma, with roasted malts.",
      "Sentence 2":
        "Remove the sentence: Very non-complex and typical for the average Impy Stout.",
      "Sentence 3": "Remove the sentence: Pretty thin and not very smooth.",
      "Sentence 4":
        "Remove the sentence: Lots of caramel and cocoa in the flavor.",
      "Sentence 5": "Remove the sentence: The alcohol is pretty obvious.",
      "None of the above": "None of the above",
    },
  },
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
      "Bachelor's degree": "Bachelor's degree",
      "Master's degree": "Master's degree",
      Doctorate: "Doctorate",
      "Professional degree": "Professional degree",
      "Prefer not to say": "Prefer not to say",
    },
  },
};
