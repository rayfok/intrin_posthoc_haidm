import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import PropTypes from "prop-types";
import * as React from "react";

MUISelect.propTypes = {
  label: PropTypes.string,
  callback: PropTypes.func,
};

export default function MUISelect(props) {
  const [value, setValue] = React.useState("");

  const handleChange = (event) => {
    setValue(event.target.value);
    props.callback(event.target.value);
  };

  return (
    <Box className={"exit-survey-short-answer"}>
      <TextField
        required
        fullWidth
        id={`short-answer-${props.label}`}
        label={props.label}
        multiline
        rows={4}
        value={value}
        onChange={handleChange}
      />
    </Box>
  );
}
