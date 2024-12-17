import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "react-oidc-context";
import { oidcConfig } from "./oidcConfig";
import HelloWorld from "./components/HelloWorld.jsx";

const App = () => {
  return (
        <Routes>
          <Route path="/" element={<HelloWorld />} />
        </Routes>
  );
};

export default App;