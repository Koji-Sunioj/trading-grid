import { useParams } from "react-router";
import { useEffect, useState } from "react";

export const ERP = () => {
  const { userModule } = useParams();
  const [authorized, setAuthorized] = useState({ message: null, state: null });

  useEffect(() => {
    authorized.state === null &&
      (async () => {
        const response = await fetch(
          import.meta.env.VITE_API + `/auth/${userModule}`,
          {
            method: "GET",
            credentials: "include",
          }
        );
        const { status } = response;

        if (status !== 200) {
          const { message } = await response.json();
          setAuthorized({ message: message, state: false });
        } else {
          setAuthorized({ message: null, state: true });
        }
      })();
  });

  console.log(authorized);
  return (
    <div>
      {authorized.state ? (
        <div>
          <div class="has-text-centered mb-4">
            <h1 class="title">This is your dashboard</h1>
            <h2 class="subtitle">Sign up with username, email and password</h2>
          </div>
          <div></div>
        </div>
      ) : (
        <div>
          <div class="has-text-centered mb-4">
            <h1 class="title">403 Forbidden</h1>
            <h2 class="subtitle">{authorized.message}</h2>
          </div>
          <div></div>
        </div>
      )}
    </div>
  );
};
