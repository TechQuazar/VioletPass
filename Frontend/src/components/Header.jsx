import React from "react";
import { Dropdown } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const USERID = 'pranav_1';

const Header = ({ auth }) => {
  const navigate = useNavigate();
  const user_id = auth?.user?.profile?.sub || USERID;
  console.log('Auth',auth)

  const handleSelect = (eventKey) => {
    if (eventKey === "my-bookings") {
      navigate("/my-bookings", { state: { user_id: user_id } });
    } else if (eventKey === "logout") {
      auth.removeUser(); // Logout logic
      console.log("User logged out");
    }
  };

  return (
    <header
      style={{
        backgroundColor: "#6f42c1",
        padding: "1rem",
        color: "white",
        position: "relative",
      }}
    >
      <h1 style={{ margin: 0, fontSize: "1.5rem" }}>VioletPass</h1>
      <div
        style={{
          position: "absolute",
          top: "50%",
          right: "1rem",
          transform: "translateY(-50%)",
        }}
      >
        {auth.isAuthenticated ? (
          <>
            {/* <pre style={{ display: "inline", marginRight: "1rem" }}>
              Hello: {auth.user?.profile["cognito:username"]}
            </pre> */}
            <Dropdown onSelect={handleSelect}>
              <Dropdown.Toggle
                id="dropdown-basic"
                style={{
                  backgroundColor: "transparent",
                  border: "none",
                  color: "white",
                  fontSize: "1rem",
                  boxShadow: "none",
                }}
              >
                {auth.user?.profile["cognito:username"]}
              </Dropdown.Toggle>
              <Dropdown.Menu align="end">
                <Dropdown.Item eventKey="my-bookings">My Bookings</Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item eventKey="logout">Logout</Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </>
        ) : (
          <button
            onClick={() => auth.signinRedirect()}
            className="btn btn-primary"
          >
            Login
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
