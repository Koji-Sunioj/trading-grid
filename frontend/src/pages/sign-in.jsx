import { Fetcher } from "../utils/utils";

import { useContext } from "react";
import { UserContext } from "../main";
import { Link, useNavigate } from "react-router";

//sign in

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

    const payload = JSON.stringify({
      username: username,
      password: password,
    });
    const fetcher = new Fetcher(
      "POST",
      import.meta.env.VITE_API + "/auth",
      payload
    );
    await fetcher.execute();
    const status = fetcher.status;
    const { message, user } = fetcher.returnBody;

    alert(message);
    if (status === 200) {
      setAuthorized({ message: "authorized", state: true, user: user });
      navigate(`/erp`);
    }
    document.getElementById("form-fieldset").disabled = false;
  };

  return (
    <div>
      <div className="has-text-centered mb-4">
        <h1 className="title">Welcome to the Trading Grid</h1>
        <h2 className="subtitle">Sign in to access your ERP modules.</h2>
      </div>
      <div>
        <div className="sign-in">
          <form onSubmit={signIn}>
            <fieldset id="form-fieldset">
              <div className="field">
                <p className="control">
                  <input
                    className="input"
                    type="text"
                    name="username"
                    placeholder="username"
                    required
                  ></input>
                </p>
              </div>
              <div className="field">
                <p className="control">
                  <input
                    className="input"
                    type="password"
                    placeholder="password"
                    name="password"
                    required
                  ></input>
                </p>
              </div>
              <div className="field">
                <p className="control">
                  <button className="button is-success">Sign in</button>
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
