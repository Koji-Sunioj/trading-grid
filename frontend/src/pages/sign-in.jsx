import { useContext } from "react";
import { UserContext } from "../main";
import { Link, useNavigate } from "react-router";

export const SignIn = () => {
  const navigate = useNavigate();
  const { setAuthorized } = useContext(UserContext);

  const signIn = async (event) => {
    document.getElementById("form-fieldset").disabled = true;
    event.preventDefault();
    const {
      target: {
        username: { value: username },
        password: { value: password },
      },
    } = event;

    const response = await fetch(import.meta.env.VITE_API + "/auth", {
      method: "POST",
      credentials: "include",
      body: JSON.stringify({
        username: username,
        password: password,
      }),
      headers: {
        "Content-Type": "text/plain",
      },
    });

    const { status } = response;
    const { message, user } = await response.json();
    alert(message);
    if (status === 200) {
      setAuthorized({ message: "authorized", state: true, user: user });
      navigate(`/erp`);
    }
    document.getElementById("form-fieldset").disabled = false;
  };

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Welcome to the Trading Grid</h1>
        <h2 class="subtitle">Sign in to access your ERP modules.</h2>
      </div>
      <div>
        <div class="sign-in">
          <form onSubmit={signIn}>
            <fieldset id="form-fieldset">
              <div class="field">
                <p class="control">
                  <input
                    class="input"
                    type="text"
                    name="username"
                    placeholder="username"
                    required
                  ></input>
                </p>
              </div>
              <div class="field">
                <p class="control">
                  <input
                    class="input"
                    type="password"
                    placeholder="password"
                    name="password"
                    required
                  ></input>
                </p>
              </div>
              <div class="field">
                <p class="control">
                  <button class="button is-success">Sign in</button>
                </p>
              </div>
            </fieldset>
          </form>
          <Link to={{ pathname: "/sign-up" }}>
            Don't have an account? Sign up
          </Link>
        </div>
      </div>
    </div>
  );
};
