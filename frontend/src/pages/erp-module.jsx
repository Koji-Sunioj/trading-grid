import { useParams } from "react-router";
import { useEffect, useState } from "react";

export const ERP = () => {
  const { module } = useParams();

  const [purchaseOrders, setPurchaseOrders] = useState(null);

  useEffect(() => {
    module === "orders" &&
      purchaseOrders === null &&
      (async () => {
        const response = await fetch(
          import.meta.env.VITE_API + `/purchase-orders/merchant`,
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
          console.log(orders);
          setPurchaseOrders(orders);
        }
      })();
  });

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">module: {module}</h1>
        <h2 class="subtitle">Click on a module below to get started.</h2>
      </div>
      <div className="po-table">
        {purchaseOrders !== null && purchaseOrders.length > 0 && (
          <table class="table">
            <thead>
              <tr>
                <th>last modified</th>
                <th>order id</th>
                <th>line count</th>
              </tr>
            </thead>
            <tbody>
              {purchaseOrders.map((order) => {
                const { modified, data, purchase_order_id } = order;
                return (
                  <tr key={purchase_order_id}>
                    <td>{modified}</td>
                    <td>{purchase_order_id}</td>
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
