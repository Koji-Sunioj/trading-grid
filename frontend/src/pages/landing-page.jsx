import { Link, useNavigate } from "react-router";

export const LandingPage = () => {
  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Welcome to the Trading Grid</h1>
        <h2 class="subtitle">Sign in to access your ERP modules.</h2>
      </div>
      <div>
        <Link to={{ pathname: "/erp/orders" }}>Purchase Orders</Link>
        <Link to={{ pathname: "/erp/shipments" }}>Purchase Orders</Link>
      </div>
    </div>
  );
};
