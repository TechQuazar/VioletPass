// import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom';
import React from 'react';
import './index.css'
import App from './App.jsx'
import { AuthProvider } from "react-oidc-context";
import { GlobalLoading} from "react-global-loading";

// const cognitoAuthConfig = {
//   authority: "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_TIpMFnsqZ",
//   client_id: "33l81qiriurkhvcic8675dqdt0",
//   redirect_uri: "http://localhost:5173",
//   response_type: "code",
//   scope: "email openid phone",
// };
const cognitoAuthConfig = {
  authority: "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_jBqBypO4C",
  client_id: "740rnmqg0gg2cmtae731k5gsvp",
  redirect_uri: "http://localhost:5173/",
  response_type: "code",
  scope: "phone openid email",
};
const cognitoAuthConfig_Admin = {
    authority: "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_azAP7ZC0h",
    client_id: "35557hd9hen3qbeidreq2a6um3",
    redirect_uri: "http://localhost:5173",
    response_type: "code",
    scope: "phone openid email",
  };

createRoot(document.getElementById('root')).render(
    <AuthProvider {...cognitoAuthConfig}>
        <BrowserRouter>
        <GlobalLoading />
            <App />
        </BrowserRouter>
    </AuthProvider>

)
