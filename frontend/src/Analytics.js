import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Label,
} from 'recharts';
import './Analytics.css'; // Optional: For styling

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

function Analytics() {
  const [aggregations, setAggregations] = useState([]);
  const [bidders, setBidders] = useState('');  // For multiple bidders
  const [providers, setProviders] = useState('');  // For multiple providers
  const [days, setDays] = useState('7');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('provider');

  useEffect(() => {
    fetchAggregations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bidders, providers, days, activeTab]);

  const fetchAggregations = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      
      // Handle multiple bidders
      if (activeTab === 'bidder' && bidders) {
        bidders.split(',').map(bidder => bidder.trim()).forEach(bidder => {
          if (bidder) params.append('bidder', bidder);
        });
      }

      // Handle multiple providers
      if (activeTab === 'provider' && providers) {
        providers.split(',').map(provider => provider.trim()).forEach(provider => {
          if (provider) params.append('provider', provider);
        });
      }

      params.append('days', days);

      const response = await fetch(
        `${API_BASE_URL}/preconfs/aggregations?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Transform the data here
      const transformedData = data.map(item => ({
        ...item,
        group_by_value: item.group_by_value.split('T')[0] // Remove time part
      }));

      setAggregations(transformedData); // Set the transformed data to state
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBiddersChange = (e) => {
    setBidders(e.target.value);  // Input as a comma-separated list
  };

  const handleProvidersChange = (e) => {
    setProviders(e.target.value);  // Input as a comma-separated list
  };

  const handleDaysChange = (e) => {
    setDays(e.target.value);
  };

  // Formatter for Y-axis to display ETH values with commas
  const yAxisFormatter = (value) => {
    return `${value.toLocaleString()} ETH`;
  };

  // Custom tooltip formatter to display ETH values
  const tooltipFormatter = (value, name) => {
    return [`${value.toLocaleString()} ETH`, name === 'total_decayed_bid' ? 'Total Bid (Decayed)' : name];
  };

  return (
    <div className="Analytics">
      <div className="tabs">
        <button
          className={activeTab === 'provider' ? 'active' : ''}
          onClick={() => setActiveTab('provider')}
        >
          Provider
        </button>
        <button
          className={activeTab === 'bidder' ? 'active' : ''}
          onClick={() => setActiveTab('bidder')}
        >
          Bidder
        </button>
      </div>

      {activeTab === 'provider' && (
        <div>
          <h2>Provider Preconf Bid Volume</h2>
          <div className="controls">
            <label htmlFor="provider">Provider Addresses (comma-separated):</label>
            <input
              type="text"
              id="provider"
              value={providers}
              onChange={handleProvidersChange}
              placeholder="Enter provider addresses"
            />

            <label htmlFor="days">Select Days:</label>
            <select id="days" value={days} onChange={handleDaysChange}>
              <option value="1">1 Day</option>
              <option value="3">3 Days</option>
              <option value="7">7 Days</option>
              <option value="30">30 Days</option>
            </select>
          </div>

          {loading && <p>Loading data...</p>}
          {error && <p style={{ color: 'red' }}>{error}</p>}

          {!loading && !error && aggregations.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={aggregations}
                margin={{ top: 20, right: 30, left: 80, bottom: 70 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="group_by_value"
                  tickFormatter={formatDate}
                  angle={-45}
                  textAnchor="end"
                  height={70}
                  interval={0}
                >
                  <Label value="Date" offset={-20} position="insideBottom" />
                </XAxis>
                <YAxis tickFormatter={yAxisFormatter}>
                  <Label
                    value="Total ETH Bid (Daily)"
                    angle={-90}
                    position="insideLeft"
                    offset={-50}
                    style={{ textAnchor: 'middle' }}
                  />
                </YAxis>
                <Tooltip formatter={tooltipFormatter} />
                <Bar dataKey="total_bid" fill="#8884d8" name="Total Bid" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            !loading && <p>No data available.</p>
          )}
        </div>
      )}

      {activeTab === 'bidder' && (
        <div>
          <h2>Bidder Preconf Bid Volume</h2>
          <div className="controls">
            <label htmlFor="bidder">Bidder Addresses (comma-separated):</label>
            <input
              type="text"
              id="bidder"
              value={bidders}
              onChange={handleBiddersChange}
              placeholder="Enter bidder addresses"
            />

            <label htmlFor="days">Select Days:</label>
            <select id="days" value={days} onChange={handleDaysChange}>
              <option value="1">1 Day</option>
              <option value="3">3 Days</option>
              <option value="7">7 Days</option>
              <option value="30">30 Days</option>
            </select>
          </div>

          {loading && <p>Loading data...</p>}
          {error && <p style={{ color: 'red' }}>{error}</p>}

          {!loading && !error && aggregations.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={aggregations}
                margin={{ top: 20, right: 30, left: 80, bottom: 70 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="group_by_value"
                  tickFormatter={formatDate}
                  angle={-45}
                  textAnchor="end"
                  height={70}
                  interval={0}
                >
                  <Label value="Date" offset={-20} position="insideBottom" />
                </XAxis>
                <YAxis tickFormatter={yAxisFormatter}>
                  <Label
                    value="Total ETH Bid (Daily)"
                    angle={-90}
                    position="insideLeft"
                    offset={-50}
                    style={{ textAnchor: 'middle' }}
                  />
                </YAxis>
                <Tooltip formatter={tooltipFormatter} />
                <Bar dataKey="total_bid" fill="#8884d8" name="Total Bid" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            !loading && <p>No data available.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default Analytics;
