import React from "react";
import "./index.css";
import "bulma/css/bulma.min.css";
import ReactDOM from "react-dom/client";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-module";
import { LandingPage } from "./pages/landing-page";
import { BrowserRouter, Routes, Route } from "react-router";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<SignIn />} />
      <Route path="/erps" element={<LandingPage />} />
      <Route path="/erps/:module" element={<ERP />} />
    </Routes>
  </BrowserRouter>
);
