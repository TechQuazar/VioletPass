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

 
// var apigClient = apigClientFactory.newClient({
//   apiKey: import.meta.env.API_KEY,
// });

const Home = () => {
  const [events, setEvents] = useState([]);
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [endedEvents, setEndedEvents] = useState([]);
  const [archivedEvents, setArchivedEvents] = useState([]); // Example for archived logic

  useEffect(() => {
    // Fetch events from the API
    const fetchEvents = async () => {
      showLoading(true)
      try {
        const response = await apigClient.eventsGet({}, {}, {});
        console.log("Response", response);
        setEvents(response.data); // Update events with the fetched data
        const data = response.data;
        const today = new Date();
        const upcoming = data.filter(
          (event) => new Date(event.end_date) > today
        );
        const ended = data.filter((event) => new Date(event.end_date) <= today);
        const archived = data.filter((event) => event.isArchived); // Example logic for archived
        setUpcomingEvents(upcoming);
        setEndedEvents(ended);
        setArchivedEvents(archived);
      } catch (error) {
        console.error("Error fetching events:", error);
      } finally{
        showLoading(false)
      }
    };

    fetchEvents(); // Trigger the fetch
  }, []);

  // State for the modal
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Open the modal with the selected event details
  const handleKnowMore = (event) => {
    setSelectedEvent(event);
    setShowModal(true);
  };

  // Close the modal
  const handleCloseModal = () => {
    setSelectedEvent(null);
    setShowModal(false);
  };

  // const handleSearch = async (searchTerm) => {
  //   try {
  //     const response = await apigClient.searchGet({ q: searchTerm }, {}, {});
  //     console.log("Search Results:", response);
  //   } catch (error) {
  //     console.error("Error during search:", error);
  //   }
  // };
  // Local search function
  const handleSearch = (searchTerm) => {
    if (!searchTerm || searchTerm.trim() === "") {
      setUpcomingEvents(
        events.filter((event) => new Date(event.end_date) > new Date())
      ); // Reset to original upcoming events
      console.log("Search reset to original upcoming events");
      return;
    }

    const filteredEvents = events.filter((event) => {
      return Object.values(event).some((value) =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      );
    });

    setUpcomingEvents(filteredEvents); // Update upcoming events with the filtered list

    console.log("Search Results:", filteredEvents);
  };

  // Navigation Hook for Redirect
  const navigate = useNavigate();

  // Redirect to Payment Success Page
  const handlePaymentSuccess = () => {
    navigate("/payment_success", {
      state: {
        name: "John Doe", // Replace with dynamic user name
        eventName: selectedEvent?.name || "Sample Event",
        tickets: 2, // Example: Number of tickets booked
        seats: ["A1", "A2"], // Example: Reserved seats
      },
    });
  };


  // Events Page Component
  const Events = () => (
    <div style={{ flex: 1, padding: "2rem", backgroundColor: "#f8f9fa" }}>
      <h2 className='mb-3'>All Events</h2>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <SearchBar onSearch={handleSearch} />
        {/* <CreateNewButton /> */}
      </div>
      <Tabs
        upcomingEvents={upcomingEvents}
        endedEvents={endedEvents}
        archivedEvents={archivedEvents}
        onKnowMore={handleKnowMore}
      />
      {/* Event Modal */}
      <EventModal
        event={selectedEvent}
        show={showModal}
        handleClose={handleCloseModal}
      />
    </div>
  );

  return (
    <Events />
  );
};

export default Home;