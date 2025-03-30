import { useState, useEffect } from "react";

export const LandingPage = () => {
  const [api, setApi] = useState(null);

  const signUp = async (event) => {
    event.preventDefault();
    const {
      target: {
        username: { value: username },
        password: { value: password },
      },
    } = event;

    const response = await fetch(
      "https://he4kvhieuh.execute-api.eu-north-1.amazonaws.com/prod/sign-up",
      {
        method: "POST",
        body: JSON.stringify({ username: username, password: password }),
      }
    );
    const something = await response.json();
    console.log(something);
  };

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Welcome to the Trading Grid</h1>
        <h2 class="subtitle">Sign in to access your ERP modules. {api}</h2>
      </div>
      <div>
        <div class="sign-in">
          <form onSubmit={signUp}>
            <fieldset>
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
                    type="email"
                    name="email"
                    placeholder="email address"
                    pattern=".+@.+\..+"
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
                  <button class="button is-success">Login</button>
                </p>
              </div>
            </fieldset>
          </form>
        </div>
      </div>
    </div>
  );
};
