import { Link } from "react-router";

export const NotFound = () => {
  return (
    <div>
      <div className="has-text-centered mb-4">
        <h1 className="title">Page not found.</h1>
        <h2 className="subtitle">
          <Link to={{ pathname: "/erp" }}>Go to landing page</Link>
        </h2>
      </div>
    </div>
  );
};
