import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainTask from "./MainTask";
import TaskSelector from "./TaskSelector";
import ReactDOM from "react-dom/client";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<TaskSelector />} />
      <Route path="task" element={<MainTask />} />
    </Routes>
  </BrowserRouter>
);
