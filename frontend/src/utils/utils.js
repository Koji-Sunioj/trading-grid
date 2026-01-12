export const determineHeaders = (module) => {
  if (module === "purchase-orders") {
    return [
      "modified",
      "client_id",
      "purchase_order_id",
      "status",
      "estimated_delivery",
      "line_count",
    ];
  } else if ((module = "dispatches")) {
    return [
      "dispatch_id",
      "purchase_order",
      "client_id",
      "estimated_delivery",
      "address",
      "status",
    ];
  }
};

export const checkDeliveryDate = (date) => {
  const today = new Date();
  const deliveryDate = new Date(date);
  return deliveryDate < today ? { color: "red" } : null;
};

export const determineNextAction = (dispatchRequest) => {
  const { estimated_delivery } = dispatchRequest;
  const deliveryDate = new Date(estimated_delivery);
  const now = new Date();

  if (now > deliveryDate) {
    return "rescheduled";
  } else if (
    deliveryDate.toISOString().substring(0, 10) ===
    now.toISOString().substring(0, 10)
  ) {
    return "handover";
  } else {
    return "no action";
  }
};
