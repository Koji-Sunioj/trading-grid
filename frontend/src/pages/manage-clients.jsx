import { Fetcher } from "../utils/utils";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

export const RoutingTable = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState(null);
  const [UIState, setUIState] = useState({ loading: false, message: null });

  const headers = ["client_id", "callback", "address", "hmac", "action"];

  useEffect(() => {
    fetchClients("fetching from server...");
  }, []);

  const fetchClients = async (message) => {
    setUIState({ loading: true, message: message });

    const fetcher = new Fetcher(
      "GET",
      import.meta.env.VITE_API + `/merchant/routing-table`
    );
    await fetcher.execute(navigate);
    const status = fetcher.status;

    if (status !== 200) {
      setClients([]);
    } else {
      const { clients } = fetcher.returnBody;
      setClients(clients);
    }
    setUIState({ loading: false, message: message });
  };

  const sendClientData = async (event) => {
    setUIState({ loading: true, message: "creating new client id" });
    event.preventDefault();
    const {
      target: {
        client_id: { value: client_id },
        callback: { value: callback },
        hmac: { value: hmac },
        address: { value: address },
      },
    } = event;

    const payload = JSON.stringify({
      client_id: client_id,
      callback: callback,
      hmac: hmac,
      address: address,
    });

    const fetcher = new Fetcher(
      "POST",
      import.meta.env.VITE_API + "/merchant/routing-table",
      payload
    );
    await fetcher.execute(navigate);
    const status = fetcher.status;
    const { message } = fetcher.returnBody;

    if (status === 200) {
      fetchClients("refreshing data...");
    }
    alert(message);
  };

  const deleteClient = async (client_id) => {
    setUIState({ loading: true, message: `deleting client id ${client_id}` });
    const fetcher = new Fetcher(
      "DELETE",
      import.meta.env.VITE_API + `/merchant/routing-table/${client_id}`
    );
    await fetcher.execute(navigate);
    const status = fetcher.status;
    const { message } = fetcher.returnBody;

    if (status === 200) {
      fetchClients("refreshing data...");
    }
    alert(message);
  };

  return (
    <div>
      <div className="has-text-centered mb-4">
        <h1 className="title">Client Management</h1>
        <h2 className="subtitle"></h2>
      </div>
      <div className="sign-in">
        <form onSubmit={sendClientData}>
          <fieldset id="form-fieldset" disabled={UIState.loading}>
            <div className="field">
              <p className="control">
                <input
                  className="input"
                  type="text"
                  name="client_id"
                  placeholder="unique client identifier"
                  required
                ></input>
              </p>
            </div>
            <div className="field">
              <p className="control">
                <input
                  className="input"
                  type="text"
                  placeholder="callback recipient url"
                  name="callback"
                  required
                ></input>
              </p>
            </div>
            <div className="field">
              <p className="control">
                <input
                  className="input"
                  type="text"
                  placeholder="HMAC key"
                  name="hmac"
                  required
                ></input>
              </p>
            </div>
            <div className="field">
              <p className="control">
                <input
                  className="input"
                  type="text"
                  placeholder="Siltakylänkuja 3, Helsinki, Finland"
                  name="address"
                  required
                ></input>
              </p>
            </div>
            <div className="field">
              <p className="control">
                <button className="button is-success">Submit</button>
              </p>
            </div>
          </fieldset>
        </form>
      </div>
      <hr />
      <div className="has-text-centered mt-2 mb-4">
        <h2 className="title">existing clients</h2>
        <h3
          className="subtitle"
          style={{ visibility: UIState.loading ? "visible" : "hidden" }}
        >
          {UIState.message}
        </h3>
      </div>
      <div className={UIState.loading ? "loading" : ""} id="loading-message">
        {clients !== null && clients.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                {headers.map((header) => (
                  <th key={header}>
                    <b>{header}</b>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {clients.map((client) => {
                const { client_id, callback, address, hmac } = client;
                return (
                  <tr key={client_id}>
                    <td>{client_id}</td>
                    <td>{callback}</td>
                    <td>{address}</td>
                    <td>{hmac}</td>
                    <td>
                      <button
                        className="action-button"
                        onClick={() => {
                          deleteClient(client_id);
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
