import React, { useEffect, useState, useRef, memo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import apigClient from "./api";
import { useAuth } from "react-oidc-context";
const USERID = "pranav_1";
import { showLoading } from "react-global-loading";

const Timer = memo(({ timeLeft }) => (
  <p>
    <strong>Time Left to Pay:</strong> {timeLeft} seconds
  </p>
));

Timer.displayName = "Timer";

const Payment = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const auth = useAuth()

  const reservationDetails = location.state?.reservationDetails || {
    eventName: "Music Festival 2024",
    lockTime: 300,
    tickets: [
      { id: "A1", category: "VIP", price: 200 },
      { id: "A2", category: "VIP", price: 200 },
    ],
    reserveId: "mock-reserve-id",
  };

  const [timeLeft, setTimeLeft] = useState(reservationDetails.lockTime);
  const [formData, setFormData] = useState({
    card_number: "",
    name_on_card: "",
    expiry_date: "",
    cvv: "",
    email:""
  });

  const timerRef = useRef(null);

  useEffect(() => {
    if (timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            alert("Time expired! Tickets are now available to others.");
            navigate("/");
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(timerRef.current);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

const handlePayment = async () => {
  const payBody = {
    reserve_id: reservationDetails.reserveId,
    card_number: formData.card_number,
    name_on_card: formData.name_on_card,
    expiry_date: formData.expiry_date,
    cvv: formData.cvv,
    event_id: reservationDetails.event.event_id,
    email_id: formData.email_id, // Add email_id here
    user_id: auth?.user?.profile?.sub || USERID, // Replace with dynamic user ID
    seat_numbers: reservationDetails.tickets.map((ticket) => ticket.seat_no),
  };

  try {
    showLoading(true)
    // Step 1: Call /pay POST to initiate the payment
    const postResponse = await apigClient.payPost({}, payBody, {});
   
    console.log('Payment Post Response',postResponse)
    const resBody = JSON.parse(postResponse.data.body); 
    const paymentId = resBody.payment_reference_id

    if (!paymentId) {
      alert("Payment initialization failed. Please try again.");
      return;
    }

    console.log("Payment initiated, payment_id:", paymentId);

    // Step 2: Call /pay GET to check the payment status
    const checkPaymentStatus = async () => {
      const getParams = { payment_id: paymentId };
      const getResponse = await apigClient.payGet(getParams, {}, {});
      return getResponse.data;
    };

    const status = await checkPaymentStatus();
    console.log('Status',status)

    if (status.status === "success") {
      alert("Payment Successful!");
      navigate("/payment_success", {
        state: {
          name: formData.name_on_card,
          eventName: reservationDetails.event.name,
          tickets: reservationDetails.tickets.length,
          seats: reservationDetails.tickets.map((ticket) => ticket.seat_no),
        },
      });
    } else if (status === "FAILURE") {
      alert("Payment failed. Please try again.");
    } else {
      alert("Unexpected payment status. Please contact support.");
    }
  } catch (error) {
    console.error("Payment error:", error);
    alert("Something went wrong. Please try again.");
  }finally{
    showLoading(false)
  }
};

  const totalPrice = reservationDetails.tickets.reduce(
    (sum, ticket) => sum + parseFloat(ticket.cost),
    0
  );

  return (
    <div
      style={{
        display: "flex",
        padding: "2rem",
        justifyContent: "space-between",
      }}
    >
      {/* Left: Payment Form */}
      <div style={{ flex: 1, paddingRight: "1rem" }}>
        <h2>Payment Details</h2>
        <form>
          <div style={{ marginBottom: "1rem" }}>
            <label>Card Number:</label>
            <input
              type="text"
              name="card_number"
              value={formData.card_number}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.5rem",
                backgroundColor: "#fff",
                color: "#000",
              }}
            />
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>Name on Card:</label>
            <input
              type="text"
              name="name_on_card"
              value={formData.name_on_card}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.5rem",
                backgroundColor: "#fff",
                color: "#000",
              }}
            />
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>Expiry Date:</label>
            <input
              type="text"
              name="expiry_date"
              value={formData.expiry_date}
              onChange={handleChange}
              placeholder="YYYY"
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.5rem",
                backgroundColor: "#fff",
                color: "#000",
              }}
            />
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>CVV:</label>
            <input
              type="text"
              name="cvv"
              value={formData.cvv}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.5rem",
                backgroundColor: "#fff",
                color: "#000",
              }}
            />
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>Email ID:</label>
            <input
              type="email"
              name="email_id"
              value={formData.email_id}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.5rem",
                backgroundColor: "#fff",
                color: "#000",
              }}
            />
          </div>
          <button
            type="button"
            onClick={handlePayment}
            disabled={timeLeft === 0}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Confirm Payment
          </button>
        </form>
      </div>

      {/* Right: Reservation Details */}
      <div
        style={{ flex: 1, paddingLeft: "1rem", borderLeft: "1px solid #ccc" }}
      >
        <h2>Reservation Details</h2>
        <Timer timeLeft={timeLeft} />
        <table
          style={{
            margin: "0 auto",
            borderCollapse: "collapse",
            width: "100%",
          }}
        >
          <thead>
            <tr>
              <th style={{ borderBottom: "1px solid #ccc", padding: "0.5rem" }}>
                Ticket ID
              </th>
              <th style={{ borderBottom: "1px solid #ccc", padding: "0.5rem" }}>
                Category
              </th>
              <th style={{ borderBottom: "1px solid #ccc", padding: "0.5rem" }}>
                Price
              </th>
            </tr>
          </thead>
          <tbody>
            {reservationDetails.tickets.map((ticket) => (
              <tr key={ticket.seat_no}>
                <td style={{ padding: "0.5rem" }}>{ticket.seat_no}</td>
                <td style={{ padding: "0.5rem" }}>{ticket.category}</td>
                <td style={{ padding: "0.5rem" }}>${ticket.cost}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p>
          <strong>Total Price:</strong> ${totalPrice}
        </p>
      </div>
    </div>
  );
};

export default Payment;
