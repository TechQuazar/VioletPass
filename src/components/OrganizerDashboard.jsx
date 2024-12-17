import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import Header from './Header';
import Tabs from './tabs';
import SearchBar from './SearchBar';
import CreateNewButton from './CreateNewButton';
import EventCard from './EventCard';
import EventModal from './EventModal';
import BookTickets from './BookTickets';
import Payment from './Payment';
import PaymentSuccess from './PaymentSuccess'; // Import PaymentSuccess
import apigClient from './api';
import MyBookings from './MyBookings';
import { showLoading } from "react-global-loading";
import AdminQRCodeScanner from './AdminQRCodeScanner';
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";


// var apigClient = apigClientFactory.newClient({
//   apiKey: import.meta.env.API_KEY,
// });
// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const Home = () => {
  const [events, setEvents] = useState([]);


  useEffect(() => {
    // Fetch events from the API
    const fetchEvents = async () => {
      showLoading(true)
      try {
        const response = await apigClient.eventsGet({}, {}, {});
        console.log("Response", response);
        setEvents(response.data); // Update events with the fetched data

      } catch (error) {
        console.error("Error fetching events:", error);
      } finally{
        showLoading(false)
      }
    };

    fetchEvents(); // Trigger the fetch
  }, []);



  const Events = () => (
  <div style={{ flex: 1, padding: "2rem", backgroundColor: "#f8f9fa" }}>
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "1rem",
      }}
    >
      <div style={{ flex: 1, marginRight: "0.5rem" }}>
        <AdminQRCodeScanner />
      </div>
      <div style={{ flex: 1, marginLeft: "0.5rem", textAlign:'center' }}>
        <CreateNewButton />
      </div>
      </div>
      <h2 className='text-center mt-5'>Event Statistics</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "1rem",
        }}
      >
        {events.map((event, index) => {
          // Pie chart data for each event
          const bookedTickets = event.total_tickets - event.available_tickets;
          const data = {
            labels: ["Tickets Available", "Tickets Booked"],
            datasets: [
              {
                data: [event.available_tickets, bookedTickets],
                backgroundColor: ["#36A2EB", "#FF6384"], // Chart colors
                hoverBackgroundColor: ["#5AB4F5", "#FF839C"], // Hover colors
              },
            ],
          };

          return (
            <div
              key={index}
              style={{
                border: "1px solid #ddd",
                padding: "1rem",
                borderRadius: "8px",
              }}
            >
              <h5 className='text-center'>{event.name}</h5>
              <Pie data={data} options={{
                maintainAspectRatio: true,
                responsive: true,
              }}
              style={{ maxHeight: "200px", maxWidth: "200px", margin: "0 auto" }} />
            </div>
          );
        })}
    </div>
    </div>
);
  return (
    <Events />
  );
};

export default Home;