import React from "react";
import "./index.css";
import "bulma/css/bulma.min.css";
import ReactDOM from "react-dom/client";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-dashboard";
import { BrowserRouter, Routes, Route } from "react-router";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<SignIn />} />
      <Route path="/erp/:userModule" element={<ERP />} />
    </Routes>
  </BrowserRouter>
);
