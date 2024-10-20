import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import './Aggregations.css'; // Optional: For styling

function Aggregations() {
  const [aggregations, setAggregations] = useState([]);
  const [groupByField, setGroupByField] = useState('bidder');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAggregations(groupByField);
  }, [groupByField]);

  const fetchAggregations = async (groupByField) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:8000/preconfs/aggregations?group_by_field=${groupByField}`
      );
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setAggregations(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGroupByChange = (e) => {
    setGroupByField(e.target.value);
  };

  return (
    <div className="Aggregations">
      <h2>Preconfs Aggregations</h2>
      <div className="controls">
        <label htmlFor="groupBy">Group By: </label>
        <select id="groupBy" value={groupByField} onChange={handleGroupByChange}>
          <option value="bidder">Bidder</option>
          {/* Add more fields as needed */}
        </select>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && !error && aggregations.length > 0 && (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={aggregations}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={groupByField} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total_bid" fill="#8884d8" name="Total Bid" />
            {/* You can add more Bars for 'average_bid', etc. */}
          </BarChart>
        </ResponsiveContainer>
      )}
      {!loading && !error && aggregations.length === 0 && <p>No data available.</p>}
    </div>
  );
}

export default Aggregations;