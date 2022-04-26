import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainTask from "./MainTask";
import TaskSelector from "./TaskSelector";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter basename="/haidm">
    <Routes>
      <Route path="/" element={<TaskSelector />} />
      <Route path="/task/" element={<MainTask />} />
    </Routes>
  </BrowserRouter>
);
