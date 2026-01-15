import { useLocation, Link, useNavigate } from "react-router";

export const NavBar = ({ authorized }) => {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  if (authorized !== null && authorized === false && pathname !== "/") {
    navigate("/");
  }

  const routes = [];

  if (pathname === "/") {
    routes.push({ path: "/", name: "home" });
  } else {
    pathname
      .split("/")
      .map((path) => "/" + path)
      .forEach((route) => {
        const newPath = pathname.substring(
          0,
          pathname.indexOf(route) + route.length
        );
        const newRoute = route === "/" ? "home" : route.replace("/", "");

        routes.push({
          path: newPath,
          name: newRoute,
        });
      });
  }

  return (
    <nav className="breadcrumb" aria-label="breadcrumbs">
      <ul>
        {routes.map((route) => (
          <li key={route.name}>
            <Link to={{ pathname: route.path }}>{route.name}</Link>
          </li>
        ))}
      </ul>
    </nav>
  );
};
