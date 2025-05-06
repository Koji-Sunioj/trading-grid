import "./index.css";
import "bulma/css/bulma.min.css";
import ReactDOM from "react-dom/client";
import { Unathorized } from "./pages/403";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-module";
import { React, createContext, useState, useEffect } from "react";
import { LandingPage } from "./pages/landing-page";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router";

export const UserContext = createContext(null);

const App = () => {
  const [authorized, setAuthorized] = useState({
    message: null,
    state: null,
    user: null,
  });

  useEffect(() => {
    authorized.state === null &&
      (async () => {
        const response = await fetch(
          import.meta.env.VITE_API + `/auth/merchant`,
          {
            method: "GET",
            credentials: "include",
          }
        );
        const { status } = response;

        if (status !== 200) {
          setAuthorized({ message: "unathorized", state: false, user: null });
        } else {
          const { user } = await response.json();
          setAuthorized({ message: "authorized", state: true, user: user });
        }
      })();
  });

  return (
    <UserContext.Provider value={authorized}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SignIn />} />
          {authorized.state && (
            <>
              <Route path="/erp" element={<LandingPage />} />
              <Route path="/erp/:module" element={<ERP />} />
            </>
          )}
          <Route path="*" element={<Unathorized />} />
        </Routes>
      </BrowserRouter>
    </UserContext.Provider>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
