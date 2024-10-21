import React, { useState, useEffect } from "react";
import "./Preconfs.css";

const API_BASE_URL = process.env.REACT_APP_API_URL;

function Preconfs() {
  const [preconfs, setPreconfs] = useState([]);
  const [selectedPreconf, setSelectedPreconf] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    fetchPreconfs();
    // eslint-disable-next-line
  }, []);

  const fetchPreconfs = async (params = {}) => {
    setLoading(true);
    setError(null);
    setIsSearching(Object.keys(params).length > 0);
    try {
      const queryParams = new URLSearchParams(params);
      const response = await fetch(`${API_BASE_URL}/preconfs?${queryParams.toString()}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setPreconfs(data.data);
    } catch (err) {
      setError(err.message);
      setPreconfs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = (preconf) => {
    setSelectedPreconf(preconf === selectedPreconf ? null : preconf);
  };

  const handleSort = (column) => {
    let newSortDirection = "asc";
    if (sortColumn === column) {
      newSortDirection = sortDirection === "asc" ? "desc" : "asc";
    }
    setSortColumn(column);
    setSortDirection(newSortDirection);

    const sortedPreconfs = [...preconfs].sort((a, b) => {
      if (a[column] < b[column]) return newSortDirection === "asc" ? -1 : 1;
      if (a[column] > b[column]) return newSortDirection === "asc" ? 1 : -1;
      return 0;
    });

    setPreconfs(sortedPreconfs);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const trimmedQuery = searchQuery.trim();

    if (!trimmedQuery) {
      // If search query is empty, fetch default preconfs
      fetchPreconfs();
      return;
    }

    // Determine if the query is a hash or a block number
    const isHash = /^0x[a-fA-F0-9]{64}$/.test(trimmedQuery);
    const isBlockNumber = /^\d+$/.test(trimmedQuery);

    if (isHash) {
      fetchPreconfs({ hash: trimmedQuery });
    } else if (isBlockNumber) {
      fetchPreconfs({ block_number_l1: trimmedQuery });
    } else {
      setError("Invalid search query. Please enter a valid hash or block number.");
      setPreconfs([]);
    }
  };

  return (
    <div className="Preconfs">
      <form onSubmit={handleSearchSubmit} className="search-form">
        <input
          type="text"
          placeholder="Search by Preconf Bid Hash or L1 Block Number"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="search-button">Search</button>
        {isSearching && (
          <button
            type="button"
            onClick={() => {
              setSearchQuery("");
              fetchPreconfs();
            }}
            className="clear-button"
          >
            Clear
          </button>
        )}
      </form>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && preconfs.length === 0 && <p>No results found.</p>}
      {!loading && !error && preconfs.length > 0 && (
        <div className="table-container">
          <table className="preconfs-table">
            <thead>
              <tr>
                <th onClick={() => handleSort("bidder")}>
                  Bidder {sortColumn === "bidder" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </th>
                <th onClick={() => handleSort("committer")}>
                  Committer {sortColumn === "committer" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </th>
                <th onClick={() => handleSort("bid")}>
                  Bid Amount {sortColumn === "bid" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </th>
                <th onClick={() => handleSort("block_number_l1")}>
                  L1 Block Number {sortColumn === "block_number_l1" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
                </th>
              </tr>
            </thead>
            <tbody>
              {preconfs.map((preconf) => (
                <React.Fragment key={preconf.commitmentIndex}>
                  <tr
                    onClick={() => handleRowClick(preconf)}
                    className={selectedPreconf === preconf ? "selected" : ""}
                  >
                    <td>{preconf.bidder}</td>
                    <td>{preconf.committer}</td>
                    <td>{preconf.bid}</td>
                    <td>{preconf.block_number_l1}</td>
                  </tr>
                  {selectedPreconf === preconf && (
                    <tr className="details-row">
                      <td colSpan="4">
                        <pre>{JSON.stringify(preconf, null, 2)}</pre>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Preconfs;
