import { useContext } from "react";
import { Link } from "react-router";
import { UserContext } from "../main";

export const LandingPage = () => {
  const { authorized } = useContext(UserContext);

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Welcome {authorized.user}</h1>
        <h2 class="subtitle">Click on a module below to get started.</h2>
      </div>
      <div class="sign-in">
        <ul>
          <li>
            <Link
              to={{
                pathname: "/erp/purchase-orders",
                search: "?sort=modified&order=asc",
              }}
            >
              Purchase Orders
            </Link>
          </li>
          <li>
            <Link to={{ pathname: "/erp/shipments" }}>Shipment Orders</Link>
          </li>
        </ul>
      </div>
    </div>
  );
};
