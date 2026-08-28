
import { Fetcher } from "./utils/utils";

import { NotFound } from "./pages/404";
import { Unathorized } from "./pages/403";

import { NavBar } from "./navbar";
import { SignIn } from "./pages/sign-in";
import { ERP } from "./pages/erp-module";
import { LandingPage } from "./pages/landing-page";
import { RoutingTable } from "./pages/manage-clients";
import { PurchaseOrder } from "./pages/purchase-order";
import { DispatchRequest } from "./pages/dispatch-request";

import "./index.css";
import "bulma/css/bulma.min.css";

import { BrowserRouter, Routes, Route } from "react-router";
import { React, createContext, useState, useEffect } from "react";

export const UserContext = createContext(null);

export const App = () => {
  const [authorized, setAuthorized] = useState({
    message: null,
    state: null,
    user: null,
    ws_token: null,
  });
  const [updatedModule, setUpdateModule] = useState({
    module: null,
    identifer: null,
  });

  const checkAuth = async () => {
    const fetcher = new Fetcher("GET", import.meta.env.VITE_API + `/auth`);
    await fetcher.execute();
    const status = fetcher.status;

    if (status !== 200) {
      setAuthorized({
        message: "unathorized",
        state: false,
        user: null,
        ws_token: null,
      });
    } else {
      const { user, ws_token } = fetcher.returnBody;
      setAuthorized({
        message: "authorized",
        state: true,
        user: user,
        ws_token: ws_token,
      });
    }
  };

  const connectWebSocket = () => {
    const websocket = new WebSocket(
      import.meta.env.VITE_WEBSOCKET +
        `?user=merchant&username=${authorized.user}&token=${authorized.ws_token}`
    );

    websocket.onopen = () => {
      console.log("Connected to WebSocket server");
      let timer = setTimeout(function tick() {
        websocket.send(
          JSON.stringify({
            action: "ping",
          })
        );
        timer = setTimeout(tick, 60000); // (*)
      }, 60000);
    };

    websocket.onclose = () => {
      console.log("server disconnected");
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.hasOwnProperty("module") && data.hasOwnProperty("identifier")) {
        setUpdateModule(JSON.parse(event.data));
      }
    };
  };

  useEffect(() => {
    if (authorized.state === null) {
      checkAuth();
    }
    if (authorized.ws_token !== null) {
      connectWebSocket();
    }
  }, [authorized]);

  return (
    <UserContext.Provider value={{ authorized, setAuthorized, updatedModule }}>
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
