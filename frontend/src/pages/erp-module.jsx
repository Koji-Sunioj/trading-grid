import { useParams } from "react-router";
import { useEffect, useState } from "react";

export const ERP = () => {
  const { module } = useParams();

  const [orders, setOrders] = useState(null);

  useEffect(() => {
    module === "orders" &&
      orders === null &&
      (async () => {
        const response = await fetch(
          import.meta.env.VITE_API + `/purchase-orders/merchant`,
          {
            method: "GET",
            credentials: "include",
          }
        );
        const { status } = response;
        setOrders([]);
        console.log(status);

        /*  if (status !== 200) {
          setAuthorized({ message: "unathorized", state: false, user: null });
        } else {
          const { user } = await response.json();
          setAuthorized({ message: "authorized", state: true, user: user });
        } */
      })();
  });

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">module: {module}</h1>
        <h2 class="subtitle">Click on a module below to get started.</h2>
      </div>
    </div>
  );
};
