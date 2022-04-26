import * as React from "react";
import PropTypes from "prop-types";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function LinearProgressWithLabel(props) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Typography
        variant="body"
        color="text.secondary"
        style={{ marginRight: "10px" }}
      >
        Progress
      </Typography>
      <div style={{ width: "70%" }}>
        <LinearProgress
          variant="determinate"
          value={(props.completed / props.total) * 100}
        />
      </div>
      <Typography
        variant="body2"
        color="text.secondary"
        style={{ marginLeft: "10px" }}
      >{`${props.completed} of ${props.total}`}</Typography>
    </div>
  );
}

LinearProgressWithLabel.propTypes = {
  /**
   * The value of the progress indicator for the determinate and buffer variants.
   * Value between 0 and 100.
   */
  completed: PropTypes.number.isRequired,
  total: PropTypes.number.isRequired,
};

export default function ProgressIndicator(props) {
  return (
    <Box sx={{ width: "100%" }}>
      <LinearProgressWithLabel
        completed={props.completed}
        total={props.total}
      />
    </Box>
  );
}
