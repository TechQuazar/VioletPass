import React, { useState } from 'react';
import EventCard from './EventCard';

const Tabs = ({ upcomingEvents, endedEvents, archivedEvents, onKnowMore }) => {
  const [activeTab, setActiveTab] = useState("Upcoming");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const tabs = ["Upcoming", "Ended"];
  const getActiveEvents = () => {
    if (activeTab === "Upcoming") return upcomingEvents;
    if (activeTab === "Ended") return endedEvents;
    if (activeTab === "Archived") return archivedEvents;
    return [];
  };
  const activeEvents = getActiveEvents();
  console.log('In Tabs',activeEvents)
  return (
    <div className="">
      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginTop: "2rem",
          justifyContent: "start",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "0.5rem 1rem",
              border: "none",
              background: activeTab === tab ? "#6f42c1" : "#ddd",
              color: activeTab === tab ? "white" : "#000",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            {tab}
          </button>
        ))}
      </div>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "1rem",
          marginTop: "2rem",
        }}
      >
        {activeEvents.map((event) => (
          <EventCard key={event.event_id} event={event} onKnowMore={onKnowMore} />
        ))}
      </div>
    </div>
  );
};

export default Tabs;