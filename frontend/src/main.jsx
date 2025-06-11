import "./index.css";
import "bulma/css/bulma.min.css";

import { NavBar } from "./navbar";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-module";
import { Unathorized } from "./pages/403";
import { LandingPage } from "./pages/landing-page";
import { RoutingTable } from "./pages/manage-clients";
import { PurchaseOrder } from "./pages/purchase-order";

import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import { React, createContext, useState, useEffect } from "react";

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
    <UserContext.Provider value={{ authorized, setAuthorized }}>
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<SignIn />} />
          {authorized.state && (
            <>
              <Route path="/erp" element={<LandingPage />} />
              <Route path="/erp/manage-clients" element={<RoutingTable />} />
              <Route path="/erp/:module" element={<ERP />} />
              <Route
                path="/erp/purchase-orders/:client_id/:purchase_order"
                element={<PurchaseOrder />}
              />
            </>
          )}
          <Route path="*" element={<Unathorized />} />
        </Routes>
      </BrowserRouter>
    </UserContext.Provider>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
