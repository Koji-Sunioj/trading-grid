import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";

export const RoutingTable = () => {
  const [clients, setClients] = useState(null);
  const [queryParams, setQueryParams] = useSearchParams();

  useEffect(() => {});

  const fetchClients = async () => {
    const response = await fetch(
      import.meta.env.VITE_API + "/admin/routing-table",
      {
        method: "GET",
        credentials: "include",
      }
    );

    const { status } = response;

    if (status !== 200) {
      alert("asd");
    } else {
      alert("asdasd");
    }
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
        method: "PUT",
        credentials: "include",
        body: JSON.stringify({
          client_id: client_id,
          callback: callback,
          hmac: hmac,
        }),
      }
    );

    const { status } = response;
    alert(status);
    /* const { message, user } = await response.json();
    alert(message);
    if (status === 200) {
      setAuthorized({ message: "authorized", state: true, user: user });
      navigate(`/erp`);
    } */
    document.getElementById("form-fieldset").disabled = false;
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
      <div className="po-table">
        {/* {purchaseOrders !== null && purchaseOrders.length > 0 && (
          <table class="table">
            <thead>
              <tr>
                {headers.map((header) => (
                  <th key={header}>
                    <button
                      onClick={() => {
                        changeQuery(header);
                      }}
                    >
                      <b>
                        {header.replace(/_/g, " ")}{" "}
                        {header === sortBy &&
                          { desc: "\u2B07", asc: "\u2B06" }[orderBy]}
                      </b>
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {purchaseOrders.map((order) => {
                const { modified, data, purchase_order_id, status } = order;
                return (
                  <tr key={purchase_order_id}>
                    <td>{modified}</td>
                    <td>{purchase_order_id}</td>
                    <td>{status}</td>
                    <td>{data.length}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )} */}
      </div>
    </div>
  );
};
