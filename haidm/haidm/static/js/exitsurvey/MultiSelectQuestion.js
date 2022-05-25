import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormGroup from "@mui/material/FormGroup";
import PropTypes from "prop-types";
import * as React from "react";

MultiSelectQuestion.propTypes = {
  context: PropTypes.string,
  prompt: PropTypes.string,
  options: PropTypes.object,
  callback: PropTypes.func,
};

export default function MultiSelectQuestion(props) {
  const [state, setState] = React.useState(
    Object.keys(props.options).reduce((a, v) => ({ ...a, [v]: false }), {})
  );

  const handleChange = (event) => {
    setState({
      ...state,
      [event.target.name]: event.target.checked,
    });
  };

  React.useEffect(() => {
    props.callback(state);
  }, [state]);

  return (
    <Box sx={{ display: "flex" }}>
      <FormControl component="fieldset" variant="standard">
        <span dangerouslySetInnerHTML={{ __html: props.context }}></span>
        <br />
        <span dangerouslySetInnerHTML={{ __html: props.prompt }}></span>
        <FormGroup>
          {Object.entries(props.options).map(([k, v]) => (
            <FormControlLabel
              key={k}
              control={
                <Checkbox checked={state[k]} onChange={handleChange} name={k} />
              }
              label={<span dangerouslySetInnerHTML={{ __html: v }}></span>}
            />
          ))}
        </FormGroup>
      </FormControl>
    </Box>
  );
}
