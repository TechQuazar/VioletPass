// src/oidcConfig.js
export const oidcConfig = {
    authority: "https://your-cognito-domain.auth.us-east-1.amazoncognito.com", // Replace with your Cognito domain
    client_id: "33l81qiriurkhvcic8675dqdt0", // Replace with your App Client ID
    redirect_uri: "http://localhost:5173", // Replace with your app's redirect URL
    post_logout_redirect_uri: "http://localhost:5173", // Replace with your app's logout URL
    response_type: "code", // Authorization Code Grant with PKCE
    scope: "openid email profile", // Scopes to request
  };