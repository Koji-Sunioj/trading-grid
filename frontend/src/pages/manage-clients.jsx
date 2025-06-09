import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";

export const RoutingTable = () => {
  const [clients, setClients] = useState(null);
  const [queryParams, setQueryParams] = useSearchParams();
  const [UIState, setUIState] = useState({ loading: false, message: null });
  const headers = ["client_id", "callback", "hmac", "action"];

  useEffect(() => {
    fetchClients("fetching from server...");
  }, []);

  const fetchClients = async (message) => {
    setUIState({ loading: true, message: message });
    const response = await fetch(
      import.meta.env.VITE_API + "/admin/routing-table",
      {
        method: "GET",
        credentials: "include",
      }
    );

    const { status } = response;

    if (status !== 200) {
      setClients([]);
    } else {
      const { clients } = await response.json();
      setClients(clients);
    }
    setUIState({ loading: false, message: null });
  };

  const sendClientData = async (event) => {
    document.getElementById("form-fieldset").disabled = true;
    event.preventDefault();
    const {
      target: {
        client_id: { value: client_id },
        callback: { value: callback },
        hmac: { value: hmac },
      },
    } = event;

    const response = await fetch(
      import.meta.env.VITE_API + "/admin/routing-table",
      {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
          client_id: client_id,
          callback: callback,
          hmac: hmac,
        }),
        headers: {
          "Content-Type": "text/plain",
        },
      }
    );

    const { status } = response;

    if (status === 200) {
      const { message } = await response.json();
      alert(message);
      fetchClients("refreshing data...");
    } else {
      alert("there was an error");
    }

    document.getElementById("form-fieldset").disabled = false;
  };

  const deleteClient = async (client_id) => {
    const response = await fetch(
      import.meta.env.VITE_API + `/admin/routing-table/${client_id}`,
      {
        method: "DELETE",
        credentials: "include",
      }
    );

    const { status } = response;
    if (status === 200) {
      const { message } = await response.json();
      alert(message);
      fetchClients("refreshing data...");
    } else {
      alert("there was an error");
    }
  };

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Client Management</h1>
        <h2 class="subtitle"></h2>
      </div>
      <div class="sign-in">
        <form onSubmit={sendClientData}>
          <fieldset id="form-fieldset">
            <div class="field">
              <p class="control">
                <input
                  class="input"
                  type="text"
                  name="client_id"
                  placeholder="unique client identifier"
                  required
                ></input>
              </p>
            </div>
            <div class="field">
              <p class="control">
                <input
                  class="input"
                  type="text"
                  placeholder="callback recipient url"
                  name="callback"
                  required
                ></input>
              </p>
            </div>
            <div class="field">
              <p class="control">
                <input
                  class="input"
                  type="text"
                  placeholder="HMAC key"
                  name="hmac"
                  required
                ></input>
              </p>
            </div>
            <div class="field">
              <p class="control">
                <button class="button is-success">Submit</button>
              </p>
            </div>
          </fieldset>
        </form>
      </div>
      <hr />
      <div class="has-text-centered mt-2">
        <h2 class="title">existing clients</h2>
        <h3
          class="subtitle"
          style={{ visibility: UIState.loading ? "visible" : "hidden" }}
        >
          {UIState.message}
        </h3>
      </div>
      <div className="po-table">
        {clients !== null && clients.length > 0 && !UIState.loading && (
          <table class="table">
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
                const { client_id, callback, hmac } = client;
                return (
                  <tr key={client_id}>
                    <td>{client_id}</td>
                    <td>{callback}</td>
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
