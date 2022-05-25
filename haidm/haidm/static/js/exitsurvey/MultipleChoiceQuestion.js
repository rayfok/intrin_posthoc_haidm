import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import PropTypes from "prop-types";
import * as React from "react";

MultipleChoiceQuestion.propTypes = {
  context: PropTypes.string,
  prompt: PropTypes.string,
  options: PropTypes.object,
  callback: PropTypes.func,
};

export default function MultipleChoiceQuestion(props) {
  const [value, setValue] = React.useState("");

  const handleChange = (event) => {
    setValue(event.target.value);
    props.callback(event.target.value);
  };

  return (
    <Box sx={{ display: "flex" }}>
      <FormControl component="fieldset" variant="standard">
        <span dangerouslySetInnerHTML={{ __html: props.context }}></span>
        <br />
        <span dangerouslySetInnerHTML={{ __html: props.prompt }}></span>

        <RadioGroup value={value} onChange={handleChange}>
          {Object.entries(props.options).map(([k, v]) => (
            <FormControlLabel
              key={k}
              value={k}
              control={<Radio />}
              label={<span dangerouslySetInnerHTML={{ __html: v }}></span>}
            />
          ))}
        </RadioGroup>
      </FormControl>
    </Box>
  );
}
