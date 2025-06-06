import { Link } from "react-router";

export const Unathorized = () => {
  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Page not found.</h1>
        <h2 class="subtitle">
          <Link to={{ pathname: "/" }}>Please sign in</Link>
        </h2>
      </div>
    </div>
  );
};
