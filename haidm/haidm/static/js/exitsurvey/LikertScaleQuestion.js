import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormLabel from "@mui/material/FormLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import PropTypes from "prop-types";
import * as React from "react";

LikertScaleQuestion.propTypes = {
  label: PropTypes.string,
  numOptions: PropTypes.number,
  options: PropTypes.arrayOf(PropTypes.string),
  callback: PropTypes.func,
};

export default function LikertScaleQuestion(props) {
  const [value, setValue] = React.useState("");

  const handleChange = (event) => {
    setValue(event.target.value);
    props.callback(event.target.value);
  };

  return (
    <Box>
      <FormControl required>
        <FormLabel id={`likert-scale-question-label-${props.label}`}>
          {props.label}
        </FormLabel>
        <RadioGroup
          row
          aria-labelledby={`likert-scale-question-label-${props.label}`}
          name={`likert-scale-question-${props.label}`}
          value={value}
          onChange={handleChange}
        >
          {props.options !== undefined
            ? props.options.map((o) => (
                <FormControlLabel
                  value={o}
                  control={<Radio />}
                  label={o}
                  key={o}
                />
              ))
            : Array.from(Array(props.numOptions).keys()).map((o) => (
                <FormControlLabel
                  value={o}
                  control={<Radio />}
                  label={o}
                  key={o}
                />
              ))}
        </RadioGroup>
      </FormControl>
    </Box>
  );
}
