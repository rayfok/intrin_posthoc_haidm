import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import PropTypes from "prop-types";
import React, { Component } from "react";

class FinishModal extends Component {
  static propTypes = {
    open: PropTypes.bool,
    submitMTurk: PropTypes.func,
  };

  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div>
        <Dialog id="finish" open={this.props.open} scroll="body" maxWidth="lg">
          <DialogTitle id="finish-title">
            {"Thank You for Completing Our Task!"}
          </DialogTitle>
          <DialogContent id="finish-description">
            <Button
              style={{ marginTop: "10px", marginBottom: "20px" }}
              variant="contained"
              color="primary"
              className="button"
              onClick={() => {
                this.props.submitMTurk();
              }}
            >
              Submit HIT
            </Button>
          </DialogContent>
        </Dialog>
      </div>
    );
  }
}

export default FinishModal;
