import React from "react";
import "./index.css";
import "bulma/css/bulma.min.css";
import ReactDOM from "react-dom/client";
import { SignUp } from "./pages/sign-up";
import { SignIn } from "./pages/sign-in";
import { ConfirmSignUp } from "./pages/confirm-sign-up";
import { BrowserRouter, Routes, Route } from "react-router";

const root = document.getElementById("root");

ReactDOM.createRoot(root).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<SignIn />} />
      <Route path="/sign-up" element={<SignUp />} />
      <Route path="/sign-up/confirm" element={<ConfirmSignUp />} />
    </Routes>
  </BrowserRouter>
);
