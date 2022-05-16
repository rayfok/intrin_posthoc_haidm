import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import PropTypes from "prop-types";
import * as React from "react";

SelectQuestion.propTypes = {
  label: PropTypes.string,
  options: PropTypes.object,
  callback: PropTypes.func,
};

export default function SelectQuestion(props) {
  const [value, setValue] = React.useState("");

  const handleChange = (event) => {
    setValue(event.target.value);
    props.callback(event.target.value);
  };

  return (
    <Box className={"exit-survey-select"}>
      <FormControl fullWidth required>
        <InputLabel id={`select-${props.label}-label`}>
          {props.label}
        </InputLabel>
        <Select
          labelId={`select-${props.label}`}
          id={`simple-select-${props.label}`}
          value={value}
          label={props.label}
          onChange={handleChange}
        >
          {Object.entries(props.options).map(([k, v]) => (
            <MenuItem value={k} key={k}>
              {v}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
}
