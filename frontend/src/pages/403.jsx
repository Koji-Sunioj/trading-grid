import { Link } from "react-router";

export const Unathorized = () => {
  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Page not found.</h1>
        <h2 class="subtitle">
          Please sign in <Link to={{ pathname: "/" }}>Purchase Orders</Link>
        </h2>
      </div>
    </div>
  );
};
