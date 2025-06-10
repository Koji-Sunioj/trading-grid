import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";

export const PurchaseOrder = () => {
  const { purchase_order } = useParams();
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
    fetchOrder(purchase_order);
  }, [purchase_order]);

  const fetchOrder = async (purchase_order) => {
    setUIState({ loading: true });
    const response = await fetch(
      import.meta.env.VITE_API + `/purchase-orders/merchant/${purchase_order}`,
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
    event.preventDefault();
    const currentForm = new FormData(event.target);
    currentForm.append("purchase_order_id", purchase_order);
    for (var pair of currentForm.entries()) {
      console.log(pair);
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
              {purchaseOrder.data.reduce(
                (prev, next) => prev + next.line_total,
                0
              )}
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
              <fieldset id="form-fieldset">
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
                      const {
                        line,
                        artist_id,
                        artist,
                        album_id,
                        album,
                        quantity,
                        line_total,
                      } = poLine;
                      return (
                        <tr key={line}>
                          <td
                            style={{
                              padding: "0px",
                              width: "10%",
                            }}
                          >
                            <input
                              style={{
                                borderRadius: "0px",
                                border: "0px",
                                display: "table-cell",
                              }}
                              class="input"
                              type="text"
                              name={`line_${line}`}
                              value={line}
                              readOnly
                            ></input>
                          </td>
                          <td>{artist_id}</td>
                          <td>{artist}</td>
                          <td>{album_id}</td>
                          <td>{album}</td>
                          <td>{quantity}</td>
                          <td>{line_total}</td>
                          <td
                            style={{
                              padding: "0px",
                              width: "10%",
                            }}
                          >
                            <input
                              style={{
                                borderRadius: "0px",
                                border: "0px",
                                color: "#7585FF",
                                display: "table-cell",
                              }}
                              class="input"
                              type="text"
                              name={`confirmed_${line}`}
                              placeholder={quantity}
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
