import React, { useState, useEffect } from "react";
import "./Preconfs.css";

const API_BASE_URL = process.env.REACT_APP_API_URL;
const PRECONFS_PER_PAGE = 50; // Number of preconfs per page

function Preconfs() {
  const [preconfs, setPreconfs] = useState([]);
  const [expandedPreconf, setExpandedPreconf] = useState(null); // Track which preconf is expanded
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [currentPage, setCurrentPage] = useState(1); // Current page number
  const [totalPages, setTotalPages] = useState(1); // Total number of pages

  useEffect(() => {
    fetchPreconfs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, searchQuery]); // Re-fetch when currentPage or searchQuery changes

  const fetchPreconfs = async (params = {}) => {
    setLoading(true);
    setError(null);
    setIsSearching(Object.keys(params).length > 0 || searchQuery.trim() !== "");

    try {
      // Merge pagination params with other search params
      const queryParams = new URLSearchParams({
        page: currentPage,
        limit: PRECONFS_PER_PAGE,
        ...params,
      });

      // If searching, include search query parameters
      if (searchQuery.trim()) {
        const trimmedQuery = searchQuery.trim();
        const isHash = /^0x[a-fA-F0-9]{64}$/.test(trimmedQuery);
        const isBlockNumber = /^\d+$/.test(trimmedQuery);

        if (isHash) {
          queryParams.set("hash", trimmedQuery);
        } else if (isBlockNumber) {
          queryParams.set("block_number_l1", trimmedQuery);
        }
      }

      const response = await fetch(`${API_BASE_URL}/preconfs?${queryParams.toString()}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();

      setPreconfs(data.data);

      // Assuming the API returns total count. Adjust based on your API's response structure.
      if (data.total) {
        setTotalPages(Math.ceil(data.total / PRECONFS_PER_PAGE));
      } else if (data.totalPages) {
        setTotalPages(data.totalPages);
      } else {
        // If total count is not available, set to current page + 1 to allow navigation
        setTotalPages(currentPage + 1);
      }
    } catch (err) {
      setError(err.message);
      setPreconfs([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = (preconf) => {
    setExpandedPreconf(expandedPreconf === preconf.commitmentIndex ? null : preconf.commitmentIndex);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const trimmedQuery = searchQuery.trim();
    setCurrentPage(1); // Reset to first page on new search

    if (!trimmedQuery) {
      fetchPreconfs();
      return;
    }

    const isHash = /^0x[a-fA-F0-9]{64}$/.test(trimmedQuery);
    const isBlockNumber = /^\d+$/.test(trimmedQuery);

    if (isHash || isBlockNumber) {
      // fetchPreconfs is already called via useEffect due to searchQuery change
      // No need to call it here
    } else {
      setError("Invalid search query. Please enter a valid hash or block number.");
      setPreconfs([]);
      setTotalPages(1);
    }
  };

  const handleTransactionDetailsClick = (e) => {
    // Prevent the click from bubbling up to the preconf-content
    e.stopPropagation();
  };

  // Handler for page navigation
  const handlePageChange = (pageNumber) => {
    if (pageNumber < 1 || pageNumber > totalPages) return;
    setCurrentPage(pageNumber);
  };

  // Generate an array of page numbers for pagination controls
  const getPageNumbers = () => {
    const pages = [];
    const maxPageButtons = 5; // Maximum number of page buttons to display
    let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2));
    let endPage = startPage + maxPageButtons - 1;

    if (endPage > totalPages) {
      endPage = totalPages;
      startPage = Math.max(1, endPage - maxPageButtons + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  return (
    <div className="Explorer">
      <form onSubmit={handleSearchSubmit} className="search-form">
        <input
          type="text"
          placeholder="Search by Preconf Bid Hash or L1 Block Number"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="search-button">
          Search
        </button>
        {(isSearching || searchQuery.trim() !== "") && (
          <button
            type="button"
            onClick={() => {
              setSearchQuery("");
              setCurrentPage(1);
            }}
            className="clear-button"
          >
            Clear
          </button>
        )}
      </form>
      {loading && <p>Loading...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && preconfs.length === 0 && <p>No results found.</p>}
      {!loading && !error && preconfs.length > 0 && (
        <>
          <div className="preconfs-list">
            {preconfs.map((preconf) => (
              <div
                key={preconf.commitmentIndex}
                className={`preconf-card ${expandedPreconf === preconf.commitmentIndex ? "expanded" : ""}`}
              >
                <div
                  className="preconf-content"
                  onClick={() => handleRowClick(preconf)}
                  style={{ cursor: "pointer" }}
                  aria-expanded={expandedPreconf === preconf.commitmentIndex}
                  role="button"
                  tabIndex={0}
                  onKeyUp={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      handleRowClick(preconf);
                    }
                  }}
                >
                  {/* Left Side: Date, Builder, Bid Hash, Bidder, and From */}
                  <div className="preconf-left">
                    <div className="preconf-date">
                      <strong>Date:</strong> {new Date(preconf.date).toLocaleString()}
                    </div>
                    <div className="preconf-builder">
                      <strong>Builder:</strong> {preconf.builder_graffiti}
                    </div>
                    <div className="preconf-bid-hash">
                      <strong>Bid Hash:</strong> {preconf.bidHash}
                    </div>
                    {/* Switch Order: Bidder First, Then From */}
                    {preconf.bidder && (
                      <div className="preconf-bidder">
                        <strong>Bidder:</strong> {preconf.bidder}
                      </div>
                    )}
                    <div className="preconf-from">
                      <strong>From:</strong>{" "}
                      <a
                        href={`https://holesky.etherscan.io/address/${preconf.from_l1}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="from-link"
                      >
                        {preconf.from_l1}
                      </a>
                    </div>
                  </div>
                  {/* Right Side: Amount and Gas Fees */}
                  <div className="preconf-right">
                    <div className="preconf-amount">
                      <strong>Amount:</strong> {parseFloat(preconf.bid_eth).toFixed(5)} ETH
                    </div>
                    <div className="preconf-gas-fees">
                      <div>
                        <strong>Max Priority Fee:</strong> {preconf.max_priority_fee_per_gas_l1} Gwei
                      </div>
                      <div>
                        <strong>Base Fee:</strong> {preconf.base_fee_per_gas_l1} Gwei
                      </div>
                    </div>
                  </div>
                </div>
                {expandedPreconf === preconf.commitmentIndex && (
                  <div className="preconf-transaction-details" onClick={handleTransactionDetailsClick}>
                    <pre>{JSON.stringify(preconf, null, 2)}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          <div className="pagination">
            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>

            {getPageNumbers().map((page) => (
              <button
                key={page}
                className={`pagination-button ${currentPage === page ? "active" : ""}`}
                onClick={() => handlePageChange(page)}
              >
                {page}
              </button>
            ))}

            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Preconfs;
