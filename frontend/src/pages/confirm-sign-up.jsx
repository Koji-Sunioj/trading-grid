import { useState, useEffect } from "react";
import { useNavigate } from "react-router";

export const ConfirmSignUp = () => {
  const navigate = useNavigate();

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Welcome to the Trading Grid</h1>
        <h2 class="subtitle">
          Confirm sign up. Check your email for verification code.
        </h2>
      </div>
      <div>
        <div class="sign-in">
          <form>
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
                  <input
                    class="input"
                    type="text"
                    placeholder="verification code"
                    name="verification"
                    pattern="[0-9]{6}"
                    required
                  ></input>
                </p>
              </div>
              <div class="field">
                <p class="control">
                  <button class="button is-success">Confirm Sign up</button>
                </p>
              </div>
            </fieldset>
          </form>
        </div>
      </div>
    </div>
  );
};
