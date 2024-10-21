// frontend/src/Preconfs.js

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

  useEffect(() => {
    fetchPreconfs();
  }, []);

  const fetchPreconfs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/preconfs?page=1&limit=10`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setPreconfs(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = (preconf) => {
    setSelectedPreconf(preconf === selectedPreconf ? null : preconf);
  };

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }

    const sortedPreconfs = [...preconfs].sort((a, b) => {
      if (a[column] < b[column]) return sortDirection === "asc" ? -1 : 1;
      if (a[column] > b[column]) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });

    setPreconfs(sortedPreconfs);
  };

  return (
    <div className="Preconfs">
      <h2>Preconfs Data</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && (
        <div className="table-container">
          <table className="preconfs-table">
            <thead>
              <tr>
                <th onClick={() => handleSort("bidder")}>Bidder</th>
                <th onClick={() => handleSort("committer")}>Committer</th>
                <th onClick={() => handleSort("bid")}>Bid Amount</th>
                <th onClick={() => handleSort("block_number_l1")}>
                  L1 Block Number
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
