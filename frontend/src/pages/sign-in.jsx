import { Link } from "react-router";

export const SignIn = () => {
  const signIn = () => {};

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
                    pattern="[A-Za-z_]{8,}"
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
                    pattern="[A-Za-z0-9]{8,}"
                    required
                  ></input>
                </p>
              </div>
              <div class="field">
                <p class="control">
                  <button class="button is-success">Sign up</button>
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
