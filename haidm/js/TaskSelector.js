import React from "react";
import { ListGroup } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

export default function TaskSelector() {
  let navigate = useNavigate();

  return (
    <div style={{ margin: "0 auto", width: "300px" }}>
      <ListGroup>
        <ListGroup.Item action onClick={() => navigate("/task?task=compas")}>
          COMPAS
        </ListGroup.Item>
        <ListGroup.Item action onClick={() => navigate("/task?task=beer")}>
          Beer Reviews
        </ListGroup.Item>
      </ListGroup>
    </div>
  );
}
