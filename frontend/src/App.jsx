import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [reviews, setReviews] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [error, setError] = useState("");

  const fetchReviews = useCallback(async () => {
    try {
      setStatus("loading");
      setError("");
      const response = await fetch(`${API_BASE_URL}/api/reviews`);
      if (!response.ok) {
        throw new Error("Failed to fetch reviews");
      }
      const data = await response.json();
      setReviews(data);
      setStatus("success");
    } catch (err) {
      console.error(err);
      setError(err.message || "Unexpected error");
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    fetchReviews();
    const interval = setInterval(fetchReviews, 15000);
    return () => clearInterval(interval);
  }, [fetchReviews]);

  const lastUpdated = useMemo(() => {
    if (!reviews.length) {
      return null;
    }
    const newest = reviews[0]?.created_at;
    return new Date(newest).toLocaleString();
  }, [reviews]);

  return (
    <div className="app-shell">
      <header>
        <div>
          <p className="eyebrow">WhatsApp Product Review Collector</p>
          <h1>All Reviews</h1>
        </div>
        <div className="actions">
          <button onClick={fetchReviews} disabled={status === "loading"}>
            {status === "loading" ? "Refreshing..." : "Refresh"}
          </button>
          {lastUpdated && (
            <p className="timestamp">Updated: {lastUpdated}</p>
          )}
        </div>
      </header>

      {status === "error" && (
        <div className="alert error">
          Could not load reviews. {error}. Try refreshing.
        </div>
      )}

      <section className="card">
        <div className="list-header">
          <span>User</span>
          <span>Product</span>
          <span>Review</span>
          <span>Timestamp</span>
        </div>

        {status === "loading" && reviews.length === 0 && (
          <p className="empty">Loading reviews...</p>
        )}

        {reviews.length === 0 && status === "success" && (
          <p className="empty">No reviews collected yet.</p>
        )}

        <ul className="review-list">
          {reviews.map((review) => (
            <li key={review.id} className="review-row">
              <span>{review.user_name}</span>
              <span>{review.product_name}</span>
              <span className="review-body">{review.product_review}</span>
              <span>
                {new Date(review.created_at).toLocaleString(undefined, {
                  hour12: false,
                })}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}


