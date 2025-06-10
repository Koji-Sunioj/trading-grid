import { useEffect, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router";

export const ERP = () => {
  const { module } = useParams();
  const [queryParams, setQueryParams] = useSearchParams();
  const [purchaseOrders, setPurchaseOrders] = useState(null);
  const [UIState, setUIState] = useState({ loading: false });

  const sortBy = queryParams.get("sort");
  const orderBy = queryParams.get("order");
  const headers = [
    "modified",
    "client_id",
    "purchase_order_id",
    "status",
    "line_count",
  ];

  const invalidParams =
    !headers.includes(sortBy) || !["asc", "desc"].includes(orderBy);

  useEffect(() => {
    if (invalidParams) {
      setQueryParams({ sort: "modified", order: "asc" });
    } else {
      fetchOrders();
    }
  }, [queryParams]);

  const fetchOrders = async () => {
    setUIState({ loading: true });
    const response = await fetch(
      import.meta.env.VITE_API +
        `/${module}/merchant?sort=${sortBy}&order=${orderBy}`,
      {
        method: "GET",
        credentials: "include",
      }
    );
    const { status } = response;

    if (status !== 200) {
      setPurchaseOrders([]);
    } else {
      const { orders } = await response.json();
      setPurchaseOrders(orders);
    }
    setUIState({ loading: false });
  };

  const changeQuery = (header) => {
    const newSortBy = orderBy === "asc" ? "desc" : "asc";
    setQueryParams({ sort: header, order: newSortBy });
  };

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">module: {module}</h1>
        <h2
          class="subtitle"
          style={{ visibility: UIState.loading ? "visible" : "hidden" }}
        >
          Fetching from server...
        </h2>
      </div>
      <div>
        {purchaseOrders !== null && purchaseOrders.length > 0 && (
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
                const { modified, client_id, data, purchase_order_id, status } =
                  order;
                return (
                  <tr key={purchase_order_id}>
                    <td>{modified}</td>
                    <td>{client_id}</td>
                    <td>
                      <Link to={`/erp/purchase-orders/${purchase_order_id}`}>
                        {purchase_order_id}
                      </Link>
                    </td>
                    <td>{status}</td>
                    <td>{data.length}</td>
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
