import { useParams } from "react-router";

export const ERP = () => {
  const { module } = useParams();

  console.log(module);
  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">This is your dashboard</h1>
        <h2 class="subtitle">Sign up with username, email and password</h2>
      </div>
      <div></div>
    </div>
  );
};
