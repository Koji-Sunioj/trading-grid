import { useContext } from "react";
import { UserContext } from "../main";
import { useParams } from "react-router";

export const ERP = () => {
  const { module } = useParams();

  return (
    <div>
      <div class="has-text-centered mb-4">
        <h1 class="title">module: {module}</h1>
        <h2 class="subtitle">Click on a module below to get started.</h2>
      </div>
    </div>
  );
};
