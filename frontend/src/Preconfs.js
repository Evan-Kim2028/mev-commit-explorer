// frontend/src/Preconfs.js

import React, { useState, useEffect } from 'react';
import './Preconfs.css';

function Preconfs() {
  const [preconfs, setPreconfs] = useState([]);
  const [selectedPreconf, setSelectedPreconf] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPreconfs();
  }, []);

  const fetchPreconfs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/preconfs?page=1&limit=10');
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

  const truncateText = (text, length = 10) => {
    return text.length > length ? `${text.slice(0, length)}...` : text;
  };

  return (
    <div className="Preconfs">
      <h2>Preconfs Data</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && !error && (
        <table className="preconfs-table">
          <thead>
            <tr>
              <th>Bidder</th>
              <th>Committer</th>
              <th>Bid Amount</th>
              <th>L1 Block Number</th>
            </tr>
          </thead>
          <tbody>
            {preconfs.map((preconf) => (
              <React.Fragment key={preconf.commitmentIndex}>
                <tr onDoubleClick={() => handleRowClick(preconf)}>
                  <td title={preconf.bidder}>{truncateText(preconf.bidder, 12)}</td>
                  <td title={preconf.committer}>{truncateText(preconf.committer, 12)}</td>
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
      )}
    </div>
  );
}

export default Preconfs;
