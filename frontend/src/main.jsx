import "./index.css";
import "bulma/css/bulma.min.css";

import { Fetcher } from "./utils/utils";

import { NavBar } from "./navbar";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-module";
import { Unathorized } from "./pages/403";
import { NotFound } from "./pages/404";
import { LandingPage } from "./pages/landing-page";
import { RoutingTable } from "./pages/manage-clients";
import { DispatchRequest } from "./pages/dispatch-request";
import { PurchaseOrder } from "./pages/purchase-order";

import ReactDOM from "react-dom/client";
import { React, createContext, useState, useEffect } from "react";
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
        const fetcher = new Fetcher("GET", import.meta.env.VITE_API + `/auth`);
        await fetcher.execute();
        const status = fetcher.status;

        if (status !== 200) {
          setAuthorized({ message: "unathorized", state: false, user: null });
        } else {
          const { user } = fetcher.returnBody;
          setAuthorized({ message: "authorized", state: true, user: user });
        }
      })();
  });

  return (
    <UserContext.Provider value={{ authorized, setAuthorized }}>
      <BrowserRouter>
        <div>
          <NavBar authorized={authorized.state} />
        </div>
        <Routes>
          <Route path="/" element={<SignIn />} />
          {authorized.state && (
            <>
              <Route path="/erp" element={<LandingPage />} />
              <Route path="/erp/manage-clients" element={<RoutingTable />} />
              <Route path="/erp/:module" element={<ERP />} />
              <Route path="/erp/:module/:client_id" element={<ERP />} />
              <Route
                path="/erp/purchase-orders/:client_id/:purchase_order"
                element={<PurchaseOrder />}
              />
              <Route
                path="/erp/dispatches/:dispatch_id/"
                element={<DispatchRequest />}
              />
            </>
          )}
          {!authorized.state && <Route path="*" element={<Unathorized />} />}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </UserContext.Provider>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
