import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import PropTypes from "prop-types";
import * as React from "react";

MUISelect.defaultProps = {
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
    <Box>
      <TextField
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
