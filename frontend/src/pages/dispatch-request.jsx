import { UserContext } from "../App";
import { Fetcher, determineNextAction } from "../utils/utils";

import { useParams, useNavigate } from "react-router";
import { useState, useEffect, useContext } from "react";

export const DispatchRequest = () => {
  const navigate = useNavigate();
  const { dispatch_id } = useParams();
  const { updatedModule } = useContext(UserContext);
  
  const [UIState, setUIState] = useState({ loading: false });
  const [dispatchRequest, setDispatchRequest] = useState(null);

  useEffect(() => {
    if (dispatchRequest === null) {
      getDispatch();
    } else if (
      dispatchRequest !== null &&
      updatedModule.module === "dispatches" &&
      updatedModule.identifier === dispatch_id
    ) {
      getDispatch();
    }
  }, [dispatch_id, updatedModule]);

  const getDispatch = async () => {
    setUIState({ loading: true });

    const fetcher = new Fetcher(
      "GET",
      import.meta.env.VITE_API + `/merchant/dispatches/${dispatch_id}`
    );
    await fetcher.execute(navigate);
    const status = fetcher.status;

    if (status !== 200) {
      setDispatchRequest({});
    } else {
      const { dispatch } = fetcher.returnBody;
      setDispatchRequest(dispatch);
    }

    setUIState({ loading: false });
  };

  const nextAction =
    dispatchRequest !== null &&
    dispatchRequest.hasOwnProperty("estimated_delivery")
      ? determineNextAction(
          dispatchRequest.estimated_delivery,
          dispatchRequest.status
        )
      : null;

  const sendDispatchUpdate = async (event) => {
    setUIState({ loading: true });
    event.preventDefault();
    const {
      target: {
        delivery: { value: delivery },
        next_status: { value: next_status },
        new_delivery: { value: new_delivery },
      },
    } = event;

    const payload = JSON.stringify({
      estimated_delivery: delivery,
      new_delivery: new_delivery.length > 0 ? new_delivery : null,
      status: next_status,
      client_id: dispatchRequest.client_id,
    });

    const fetcher = new Fetcher(
      "POST",
      import.meta.env.VITE_API + `/merchant/dispatches/${dispatch_id}`,
      payload
    );
    await fetcher.execute(navigate);

    getDispatch(dispatch_id);
    setUIState({ loading: false });
  };

  const hasNewDeliveryDate =
    dispatchRequest !== null &&
    dispatchRequest.hasOwnProperty("new_delivery_date");

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
                      value={dispatchRequest.estimated_delivery}
                      style={{ textAlign: "center" }}
                      disabled
                    ></input>
                  </p>
                </div>
                <div style={{ display: hasNewDeliveryDate ? "block" : "none" }}>
                  <label class="label">new delivery date</label>
                  <div className="field">
                    <p className="control">
                      <input
                        className="input"
                        type="text"
                        name="new_delivery"
                        value={
                          hasNewDeliveryDate
                            ? dispatchRequest.new_delivery_date
                            : ""
                        }
                        style={{ textAlign: "center" }}
                        disabled
                      ></input>
                    </p>
                  </div>
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
                {["shipped", "rescheduled"].includes(nextAction) && (
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
                      {dispatchRequest.estimated_delivery} is past due. The next
                      when you submit this request, the new date will be saved
                      and updated at the client.
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
