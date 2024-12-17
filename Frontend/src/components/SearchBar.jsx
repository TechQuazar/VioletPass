import React, { useState } from "react";
import { Form, Button, InputGroup } from "react-bootstrap";

const SearchBar = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearch = () => {
    // Call the onSearch function with the search term
    if (onSearch) onSearch(searchTerm);
  };

  return (
    <InputGroup className="" style={{ maxWidth: "50%" }}>
      <Form.Control
        type="text"
        placeholder="Search by event name..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <Button variant="primary" onClick={handleSearch} >
        Search
      </Button>
    </InputGroup>
  );
};

export default SearchBar;
