import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate , useNavigate} from "react-router-dom";
import { useAuth } from "react-oidc-context";

import "bootstrap/dist/css/bootstrap.min.css";
import Header from "./components/Header";
import Home from "./components/Home";
import OrganizerDashboard from "./components/OrganizerDashboard";
import BookTickets from "./components/BookTickets";
import Payment from "./components/Payment";
import PaymentSuccess from "./components/PaymentSuccess";
import NotFound from "./components/NotFound"; // Fallback for undefined routes
import MyBookings from "./components/MyBookings";

// Main App Component
const App = () => {
  const auth = useAuth();
  const [isAdmin,setIsAdmin] = useState(false)
  const navigate = useNavigate();

  //setIsAdmin(auth.user?.profile?.["cognito:groups"][0]?true:false)
  // setIsAdmin(auth.user?.profile?.["cognito:groups"]?.includes("Admin"));
  const [userGroups, setUserGroups] = useState([]);
  const [isLoadingGroups, setIsLoadingGroups] = useState(false);

  // Fetch user groups from the Cognito ID token after login
  useEffect(() => {
    const fetchUserGroups = async () => {
      console.log('Use EFfect!')
      if (auth.isAuthenticated) {
        setIsLoadingGroups(true)
        try {
          const groups = auth.user?.profile?.["cognito:groups"] || []; // Get groups from Cognito
          setIsAdmin(auth.user?.profile?.["cognito:groups"]?.includes("Admin"));
          console.log('Groups',groups)
          setUserGroups(groups);
        } catch (error) {
          console.error("Error fetching user groups:", error);
        } finally {
          setIsLoadingGroups(false);
        }
      }
    };
    

    fetchUserGroups();
  }, [auth.isAuthenticated, auth.user]);
  // useEffect(() => {
  //   if (isAdmin) {
  //     navigate("/organizer-dashboard");
  //   }
  // }, 
  // [isAdmin, navigate]);
  // Loading Screen While Groups or Auth Are Loading
  if (auth.isLoading || isLoadingGroups) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <h2>Loading...</h2>
      </div>
    );
  }

  // Error Handling
  if (auth.error) {
    return (
      <div style={{ textAlign: "center", marginTop: "50px" }}>
        <h2>Error: {auth.error.message}</h2>
      </div>
    );
  }

  // Protected Route Wrapper for Authentication
  const ProtectedRoute = ({ children, allowedGroups = [] }) => {
    if (!auth.isAuthenticated) {
      auth.signinRedirect();
      return <div>Redirecting to login...</div>;
    }

    // Role-based Access Control (if `allowedGroups` is defined)
    console.log('Allowerd Groups',allowedGroups)
    console.log('Condition', userGroups)
    if (allowedGroups.length > 0 && !userGroups.some((group) => allowedGroups.includes(group))) {
      print('Inside!!!!!!!!!!!')
      return <Navigate to="/" replace />; // Redirect unauthorized users to the Home page
    }
    return children;
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <Header auth={auth} /> {/* Pass `auth` to the Header component for login/logout logic */}
      <Routes>

        {/* Public Route */}
        <Route
  path="/"
  element={
    isAdmin ? <OrganizerDashboard /> : <Home />
  }
/>        
        {/* Organizer Protected Route */}
        {/* <Route
          path="/organizer-dashboard"
          element={
            <ProtectedRoute allowedGroups={["Admin"]}>
              <OrganizerDashboard />
            </ProtectedRoute>
          }
        /> */}
        <Route path="/my-bookings" element={<ProtectedRoute>
              <MyBookings />
            </ProtectedRoute>} />

        {/* Book Tickets (Accessible to All Authenticated Users) */}
        <Route
          path="/book-ticket"
          element={
            <ProtectedRoute>
              <BookTickets />
            </ProtectedRoute>
          }
        />

        {/* Payment Process */}
        <Route
          path="/payment"
          element={
            <ProtectedRoute>
              <Payment />
            </ProtectedRoute>
          }
        />

        {/* Payment Success */}
        <Route
          path="/payment_success"
          element={
            <ProtectedRoute>
              <PaymentSuccess />
            </ProtectedRoute>
          }
        />
        

        {/* Catch-All for Undefined Routes */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
};

export default App;