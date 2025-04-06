import { useNavigate } from "react-router";

export const ConfirmSignUp = () => {
  const navigate = useNavigate();

  const confirmSignUp = async (event) => {
    document.getElementById("form-fieldset").disabled = true;
    event.preventDefault();
    const {
      target: {
        username: { value: username },
        verification: { value: verification },
      },
    } = event;

    const response = await fetch(
      "https://74s7sl8n76.execute-api.eu-north-1.amazonaws.com/prod/sign-up",
      {
        method: "PATCH",
        body: JSON.stringify({
          username: username,
          verification: verification,
        }),
      }
    );

    const { status } = response;
    const { message } = await response.json();
    alert(message);
    if (status === 200) {
      navigate("/");
    }
    document.getElementById("form-fieldset").disabled = false;
  };

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
          <form onSubmit={confirmSignUp}>
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
