import { determineNextAction } from "../utils/utils";

import { useParams } from "react-router";
import { useState, useEffect } from "react";

export const DispatchRequest = () => {
  const { dispatch_id } = useParams();
  const [dispatchRequest, setDispatchRequest] = useState(null);
  const [UIState, setUIState] = useState({ loading: false });

  useEffect(() => {
    getDispatch(dispatch_id);
  }, [dispatch_id]);

  const getDispatch = async (dispatch_id) => {
    setUIState({ loading: true });

    const response = await fetch(
      import.meta.env.VITE_API + `/merchant/dispatches/${dispatch_id}`,
      {
        credentials: "include",
      }
    );
    const { status } = response;

    if (status !== 200) {
      setDispatchRequest({});
    } else {
      const { dispatch } = await response.json();
      setDispatchRequest(dispatch);
    }

    setUIState({ loading: false });
  };

  const nextAction =
    dispatchRequest !== null &&
    dispatchRequest.hasOwnProperty("estimated_delivery")
      ? determineNextAction(dispatchRequest)
      : null;

  const sendDispatchUpdate = async (event) => {
    setUIState({ loading: true });
    event.preventDefault();
    const {
      target: {
        delivery: { value: delivery },
        next_status: { value: next_status },
      },
    } = event;

    const response = await fetch(
      import.meta.env.VITE_API + `/merchant/dispatches/${dispatch_id}`,
      {
        credentials: "include",
        method: "POST",
        body: JSON.stringify({
          estimated_delivery: delivery,
          status: next_status,
          client_id: dispatchRequest.client_id,
        }),
      }
    );

    const { message } = await response.json();
    alert(message);
    getDispatch(dispatch_id);
    setUIState({ loading: false });
  };

  return (
    <div>
      <div className="has-text-centered mb-2">
        <h2
          className="subtitle"
          style={{ visibility: UIState.loading ? "visible" : "hidden" }}
        >
          Fetching from server...
        </h2>
      </div>
      {dispatchRequest !== null &&
        dispatchRequest.hasOwnProperty("client_id") && (
          <>
            <div className="has-text-centered mb-4">
              <h2 className="subtitle mb-1">
                client: {dispatchRequest.client_id}
              </h2>
              <h2 className="subtitle mb-1">
                status: {dispatchRequest.status}
              </h2>
              <h2 className="subtitle mb-1">
                address: {dispatchRequest.address}
              </h2>
              <h2 className="subtitle mb-1">
                purchase order: {dispatchRequest.purchase_order}
              </h2>
            </div>
            <form className="sign-in" onSubmit={sendDispatchUpdate}>
              <fieldset id="form-fieldset" disabled={UIState.loading}>
                <label class="label">current delivery date</label>
                <div className="field">
                  <p className="control">
                    <input
                      className="input"
                      type="text"
                      name="delivery"
                      value={
                        dispatchRequest.hasOwnProperty("new_delivery_date")
                          ? dispatchRequest.new_delivery_date
                          : dispatchRequest.estimated_delivery
                      }
                      style={{ textAlign: "center" }}
                      disabled
                    ></input>
                  </p>
                </div>
                <label class="label">next status</label>
                <div className="field">
                  <p className="control">
                    <input
                      className="input"
                      type="text"
                      name="next_status"
                      value={nextAction}
                      disabled
                      style={{ textAlign: "center" }}
                    ></input>
                  </p>
                </div>
                {["handover", "rescheduled"].includes(nextAction) && (
                  <div className="field">
                    <p className="control">
                      <button className="button is-success">submit</button>
                    </p>
                  </div>
                )}
                {dispatchRequest.hasOwnProperty("new_delivery_date") && (
                  <article class="message is-danger mt-2">
                    <div class="message-body">
                      This dispatch must be rescheduled since old date{" "}
                      {dispatchRequest.estimated_delivery} is past due. when you
                      submit this request, the new date will be saved and
                      updated at the client.
                    </div>
                  </article>
                )}
              </fieldset>
            </form>
          </>
        )}
    </div>
  );
};
