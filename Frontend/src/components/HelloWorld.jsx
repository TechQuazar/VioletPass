// src/HelloWorld.jsx
import React from "react";
import { useAuth } from "react-oidc-context";

const HelloWorld = () => {
  const auth = useAuth();

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (auth.error) {
    return <div>Error: {auth.error.message}</div>;
  }

  return (
    <div style={{ textAlign: "center", marginTop: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Hello World</h1>
      {auth.isAuthenticated ? (
        <div>
          <p>Welcome, {auth.user?.profile.email}!</p>
          <button
            onClick={() => auth.signoutRedirect()}
            style={{
              backgroundColor: "#ff4b5c",
              color: "white",
              border: "none",
              padding: "10px 20px",
              cursor: "pointer",
              borderRadius: "5px",
            }}
          >
            Logout
          </button>
        </div>
      ) : (
        <button
          onClick={() => auth.signinRedirect()}
          style={{
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            padding: "10px 20px",
            cursor: "pointer",
            borderRadius: "5px",
          }}
        >
          Login
        </button>
      )}
    </div>
  );
};

export default HelloWorld;