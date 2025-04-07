import React from "react";
import "./index.css";
import "bulma/css/bulma.min.css";
import ReactDOM from "react-dom/client";
import { SignUp } from "./pages/sign-up";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-dashboard";
import { ConfirmSignUp } from "./pages/confirm-sign-up";
import { BrowserRouter, Routes, Route } from "react-router";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<SignIn />} />
      <Route path="/sign-up" element={<SignUp />} />
      <Route path="/sign-up/confirm" element={<ConfirmSignUp />} />
      <Route path="/erp/:module" element={<ERP />} />
    </Routes>
  </BrowserRouter>
);
