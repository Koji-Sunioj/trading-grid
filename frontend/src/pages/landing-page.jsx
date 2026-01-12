import { useContext } from "react";
import { Link } from "react-router";
import { UserContext } from "../main";

export const LandingPage = () => {
  const { authorized } = useContext(UserContext);

  return (
    <div>
      <div className="has-text-centered mb-4">
        <h1 className="title">Welcome {authorized.user}</h1>
        <h2 className="subtitle">Click on a module below to get started.</h2>
      </div>
      <div className="sign-in">
        <ul>
          <li>
            <Link
              to={{
                pathname: "/erp/purchase-orders",
                search: "?sort=modified&order=desc",
              }}
            >
              Purchase Orders
            </Link>
          </li>
          <li>
            <Link to={{ pathname: "/erp/dispatches" }}>Shipment Orders</Link>
          </li>
        </ul>
      </div>
      <section className="section">
        <div className="has-text-centered mb-4">
          <h2 className="title">Manage clients</h2>
          <h2 className="subtitle">
            Routings, authentication and identifiers.
          </h2>
        </div>
        <div className="sign-in">
          <ul>
            <li>
              <Link to={{ pathname: "/erp/manage-clients" }}>
                Client Management
              </Link>
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
};
