import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";

export const PurchaseOrder = () => {
  const { purchase_order, client_id } = useParams();
  const [purchaseOrder, setPurchaseOrder] = useState(null);
  const [UIState, setUIState] = useState({ loading: false });

  const headers = [
    "line",
    "artist_id",
    "artist",
    "album_id",
    "album",
    "quantity",
    "line_total",
    "confirmed",
  ];

  useEffect(() => {
    fetchOrder();
  }, [purchase_order]);

  const fetchOrder = async () => {
    setUIState({ loading: true });
    const response = await fetch(
      import.meta.env.VITE_API +
        `/merchant/purchase-orders/${client_id}/${purchase_order}`,
      {
        method: "GET",
        credentials: "include",
      }
    );
    const { status } = response;
    if (status !== 200) {
      setPurchaseOrder({});
    } else {
      const { purchase_order } = await response.json();
      setPurchaseOrder(purchase_order);
    }
    setUIState({ loading: false });
  };

  const sendConfirmation = async (event) => {
    setUIState({ loading: true });
    event.preventDefault();
    const currentForm = new FormData(event.target);

    const payload = {
      purchase_order_id: Number(purchase_order),
      client_id: purchaseOrder.client_id,
      lines: [],
    };

    const indexes = [
      ...new Set(
        Array.from(currentForm.entries()).map((entry) =>
          Number(entry[0].split("_")[1])
        )
      ),
    ];

    indexes.forEach((index) => {
      payload.lines.push({
        line: Number(currentForm.get(`line_${index}`)),
        confirmed: Number(currentForm.get(`confirmed_${index}`)),
        album_id: Number(currentForm.get(`album_${index}`)),
      });
    });

    const response = await fetch(
      import.meta.env.VITE_API +
        `/merchant/purchase-orders/${client_id}/${purchase_order}`,
      {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(payload),
      }
    );
    const { status } = response;

    if (status === 200) {
      alert(
        `purchase order ${purchase_order} has been updated at ${client_id}'s server`
      );
      fetchOrder();
    } else {
      const { message } = await response.json();
      alert(message);
    }

    setUIState({ loading: false });
  };

  const controlQuantity = (event, htmlLine) => {
    event.preventDefault();
    const lines = [...purchaseOrder["data"]];
    const line = lines.find((line) => line.line === Number(htmlLine));
    if (Number(event.target.value) > line.quantity) {
      event.target.value = "";
    }
  };

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">purchase-order: {purchase_order}</h1>
        <h2
          class="subtitle"
          style={{ visibility: UIState.loading ? "visible" : "hidden" }}
        >
          Fetching from server...
        </h2>
      </div>

      {purchaseOrder !== null && purchaseOrder.hasOwnProperty("client_id") && (
        <>
          <div class="has-text-centered mb-4">
            <h2 class="subtitle mb-1">client: {purchaseOrder.client_id}</h2>
            <h2 class="subtitle mb-1">
              order total:{" "}
              {purchaseOrder.data
                .reduce((prev, next) => prev + next.line_total, 0)
                .toFixed(2)}
            </h2>
            <h2 class="subtitle mb-1">status: {purchaseOrder.status}</h2>
            <h2 class="subtitle mb-1">modified: {purchaseOrder.modified}</h2>
          </div>
          <div>
            <hr />
            <div class="has-text-centered mt-2 mb-4">
              <h2 class="title">order lines</h2>
            </div>
            <form onSubmit={sendConfirmation}>
              <fieldset
                id="form-fieldset"
                disabled={
                  UIState.loading || purchaseOrder.status === "confirmed"
                }
              >
                <table class="table">
                  <thead>
                    <tr>
                      {headers.map((header) => (
                        <td key={header}>{header.replace("_", " ")}</td>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {purchaseOrder.data.map((poLine) => {
                      return (
                        <tr key={poLine.line}>
                          <td className="td-input">
                            <input
                              class="input"
                              type="text"
                              name={`line_${poLine.line}`}
                              value={poLine.line}
                              readOnly
                            ></input>
                          </td>
                          <td>{poLine.artist_id}</td>
                          <td>{poLine.artist}</td>
                          <td className="td-input">
                            <input
                              class="input"
                              type="text"
                              name={`album_${poLine.line}`}
                              value={poLine.album_id}
                              readOnly
                            ></input>
                          </td>
                          <td>{poLine.album}</td>
                          <td>{poLine.quantity}</td>
                          <td>{poLine.line_total}</td>
                          <td className="td-input">
                            <input
                              style={{
                                color: "red",
                              }}
                              class="input"
                              type="text"
                              name={`confirmed_${poLine.line}`}
                              placeholder={poLine.quantity}
                              defaultValue={
                                poLine.hasOwnProperty("confirmed")
                                  ? poLine.confirmed
                                  : undefined
                              }
                              onChange={(event) => {
                                controlQuantity(event, poLine.line);
                              }}
                              required
                            ></input>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <div class="field has-text-centered">
                  <p class="control">
                    <button class="button is-success">
                      submit confirmation
                    </button>
                  </p>
                </div>
              </fieldset>
            </form>
          </div>
        </>
      )}
    </div>
  );
};
