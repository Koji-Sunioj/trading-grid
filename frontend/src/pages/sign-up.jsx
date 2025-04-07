import { useNavigate } from "react-router";

export const SignUp = () => {
  const navigate = useNavigate();

  const signUp = async (event) => {
    document.getElementById("form-fieldset").disabled = true;
    event.preventDefault();
    const {
      target: {
        username: { value: username },
        password: { value: password },
        email: { value: email },
      },
    } = event;

    const response = await fetch(import.meta.env.VITE_API + "/sign-up", {
      method: "POST",
      body: JSON.stringify({
        username: username,
        password: password,
        email: email,
      }),
    });
    const { status } = response;
    const { message } = await response.json();
    alert(message);

    if (status === 200) {
      navigate("/sign-up/confirm");
    }
    document.getElementById("form-fieldset").disabled = false;
  };

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">Welcome to the Trading Grid</h1>
        <h2 class="subtitle">Sign up with username, email and password</h2>
      </div>
      <div>
        <div class="sign-in">
          <form onSubmit={signUp}>
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
