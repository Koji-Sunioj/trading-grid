import { determineHeaders } from "../utils/utils";
import { useEffect, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router";

export const ERP = () => {
  const { module, client_id } = useParams();
  const [queryParams, setQueryParams] = useSearchParams();

  const [dispatches, setDispatches] = useState(null);
  const [purchaseOrders, setPurchaseOrders] = useState(null);
  const [UIState, setUIState] = useState({ loading: false });

  const sortBy = queryParams.get("sort");
  const orderBy = queryParams.get("order");
  const headers = determineHeaders(module);

  const invalidParams =
    !headers.includes(sortBy) || !["asc", "desc"].includes(orderBy);

  useEffect(() => {
    if (invalidParams && module === "purchase-orders") {
      setQueryParams({ sort: "modified", order: "desc" });
    } else if (invalidParams && module === "dispatches") {
      setQueryParams({ sort: "estimated_delivery", order: "desc" });
    } else {
      fetchOrders();
    }
  }, [queryParams]);

  const fetchOrders = async () => {
    setUIState({ loading: true });

    let endpoint = `/merchant/${module}?sort=${sortBy}&order=${orderBy}`;
    if (client_id !== undefined) {
      endpoint += `&client_id=${client_id}`;
    }

    const response = await fetch(import.meta.env.VITE_API + endpoint, {
      method: "GET",
      credentials: "include",
    });
    const { status } = response;

    switch (module) {
      case "purchase-orders":
        if (status !== 200) {
          setPurchaseOrders([]);
        } else {
          const { orders } = await response.json();
          setPurchaseOrders(orders);
        }
        break;
      case "dispatches":
        if (status !== 200) {
          setPurchaseOrders([]);
        } else {
          const { dispatches } = await response.json();
          setDispatches(dispatches);
        }
        break;
    }
    setUIState({ loading: false });
  };

  const changeQuery = (header) => {
    const newSortBy = orderBy === "asc" ? "desc" : "asc";
    setQueryParams({ sort: header, order: newSortBy });
  };

  const renderPOS =
    purchaseOrders !== null &&
    purchaseOrders.length > 0 &&
    module === "purchase-orders";

  const renderDispatches =
    dispatches !== null && dispatches.length > 0 && module === "dispatches";

  const renderHeader = renderDispatches || renderPOS;

  return (
    <div>
      <div className="has-text-centered mb-4">
        <h1 className="title">module: {module}</h1>
        <h2
          className="subtitle"
          style={{ visibility: UIState.loading ? "visible" : "hidden" }}
        >
          Fetching from server...
        </h2>
      </div>
      <div>
        <table className="table">
          {renderHeader && (
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
          )}
          {renderDispatches && (
            <tbody>
              {dispatches.map((dispatch) => {
                const {
                  dispatch_id,
                  purchase_order,
                  client_id,
                  estimated_delivery,
                  status,
                  address,
                } = dispatch;
                return (
                  <tr key={dispatch_id}>
                    <td>
                      {!status.includes(["shipped", "received"]) ? (
                        <Link to={`/erp/dispatches/${dispatch_id}`}>
                          {dispatch_id}
                        </Link>
                      ) : (
                        { dispatch_id }
                      )}
                    </td>
                    <td>
                      <Link
                        to={`/erp/purchase-orders/${client_id}/${purchase_order}`}
                      >
                        {purchase_order}
                      </Link>
                    </td>
                    <td>{client_id}</td>
                    <td>{estimated_delivery}</td>
                    <td>{status}</td>
                    <td>{address}</td>
                  </tr>
                );
              })}
            </tbody>
          )}
          {renderPOS && (
            <tbody>
              {purchaseOrders.map((order) => {
                const {
                  modified,
                  client_id,
                  data,
                  purchase_order_id,
                  status,
                  estimated_delivery,
                } = order;
                return (
                  <tr key={purchase_order_id}>
                    <td>{modified}</td>
                    <td>
                      <Link to={`/erp/${module}/${client_id}`}>
                        {client_id}
                      </Link>
                    </td>
                    <td>
                      <Link
                        to={`/erp/purchase-orders/${client_id}/${purchase_order_id}`}
                      >
                        {purchase_order_id}
                      </Link>
                    </td>
                    <td>{status}</td>
                    <td>{estimated_delivery}</td>
                    <td>{data.length}</td>
                  </tr>
                );
              })}
            </tbody>
          )}
        </table>
      </div>
    </div>
  );
};
