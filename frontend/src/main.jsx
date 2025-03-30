import React from "react";
import "./index.css";
import "bulma/css/bulma.min.css";
import ReactDOM from "react-dom/client";
import { LandingPage } from "./pages/landing";
import { BrowserRouter, Routes, Route } from "react-router";

const root = document.getElementById("root");

ReactDOM.createRoot(root).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<LandingPage />} />
    </Routes>
  </BrowserRouter>
);
