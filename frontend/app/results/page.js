"use client";

import Header from "../components/Header";
import Link from "next/link";
import { useData } from "../context/dataContext";
import { useState, useRef, useEffect } from "react";

// StarRating component with toggle behavior.
// Clicking a star that’s already selected toggles off (rating becomes 0).


const ResultsPage = () => {
  const { sharedData } = useData();
  const [numMissing, setNumMissing] = useState(0);
  const cardRefs = useRef([]);
  const [maxHeight, setMaxHeight] = useState(0);

  // State to hold ratings and comments.
  // Structure: { [id]: { rating: number, comment: string } }
  const [ratingsData, setRatingsData] = useState({});
  

  const StarRating = ({ id, rating, onRatingChange }) => {

    return (
      <div>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            style={{ cursor: "pointer", fontSize: "1.5rem" }}
            onClick={() => onRatingChange(id, rating === star ? 0 : star)}
          >
            {star <= rating ? "★" : "☆"}
          </span>
        ))}
      </div>
    );
  };

  // Callback ref that assigns the element and checks if all refs are collected.
  const setCardRef = (el, index) => {
    if (el) {
      cardRefs.current[index] = el;
      if (
        cardRefs.current.filter(Boolean).length ===
        sharedData.length - numMissing
      ) {
        const heights = cardRefs.current.filter(Boolean).map((ref) => ref.clientHeight);
        const newMaxHeight = Math.max(...heights);
        if (newMaxHeight !== maxHeight) {
          setMaxHeight(newMaxHeight);
        }
      }
    }
  };

  // Handle star rating change for a recommendation.
  const handleRatingChange = (id, rating) => {
    setRatingsData((prev) => ({
      ...prev,
      [id]: {
        ...prev[id],
        rating: rating,
      },
    }));
  };

  // Handle comment change for a recommendation.
  // Comments can only be updated if a rating exists.
  const handleCommentChange = (id, comment) => {
    if (!ratingsData[id] || !ratingsData[id].rating) {
      alert("Please add a rating first before adding a comment.");
      return;
    }
    setRatingsData((prev) => ({
      ...prev,
      [id]: {
        ...prev[id],
        comment: comment,
      },
    }));
  };

  // Passive submission: use useEffect to send ratings when the user leaves the page.
  useEffect(() => {
    const handleBeforeUnload = (event) => {
      // Prepare payload: include only items with a rating.
      const payload = Object.entries(ratingsData)
        .filter(([id, data]) => data.rating)
        .map(([id, data]) => ({
          id,
          rating: data.rating,
          comment: data.comment || "",
        }));

      if (payload.length > 0) {
        const url = "/api/submitRatings";
        const dataBlob = new Blob([JSON.stringify({ ratings: payload })], {
          type: "application/json",
        });

        // Use sendBeacon for asynchronous, non-blocking submission.
        if (navigator.sendBeacon) {
          navigator.sendBeacon(url, dataBlob);
        } else {
          // Fallback to fetch if necessary.
          fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ratings: payload }),
          });
        }
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [ratingsData]);

  if (!sharedData || sharedData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <Header onSignOut={() => {}} isLoading={false} />
        <p className="text-gray-600 text-xl">No results found.</p>
      </div>
    );
  }
  console.log(ratingsData)
  return (
    <div className="min-h-screen bg-gray-100">
      <Header onSignOut={() => {}} isLoading={false} />
      <div className="pt-20 mt-10 px-60">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {sharedData.map((result, index) => {
            // Use result.id if available; otherwise, fallback to index.
            const id = result.id || index;
            if (
              !result.image_url ||
              !result.title ||
              !result.image_url.startsWith("http")
            ) {
              setNumMissing(numMissing + 1);
              return null;
            }

            const currentRating = ratingsData[id]?.rating || 0;
            const currentComment = ratingsData[id]?.comment || "";

            return (
              <div key={id} className="flex flex-col">
                <Link href={result.url} target="_blank" rel="noopener noreferrer">
                  <div
                    ref={(el) => setCardRef(el, index)}
                    className="bg-white shadow-md rounded-lg overflow-hidden cursor-pointer hover:shadow-lg transition flex flex-col"
                    style={{ height: maxHeight || "auto" }}
                  >
                    <img
                      src={result.image_url}
                      alt={result.title}
                      className="w-auto h-80 object-cover"
                      loading="lazy"
                    />
                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <h2
                        className="text-lg font-semibold text-gray-800 line-clamp-2 overflow-hidden"
                        style={{
                          display: "-webkit-box",
                          WebkitBoxOrient: "vertical",
                          WebkitLineClamp: 2,
                        }}
                      >
                        {result.title}
                      </h2>
                      <p className="text-sm font-medium text-blue-600">
                        Confidence Score:{" "}
                        {result.score
                          ? `${result.score.toFixed(2)}%`
                          : "N/A"}
                      </p>
                    </div>
                  </div>
                </Link>

                {/* Star Rating System */}
                <div className="mt-2 flex justify-center">
                  <StarRating
                    rating={currentRating}
                    onRatingChange={handleRatingChange}
                    id={id}
                  />
                </div>

                {/* Comment Input */}
                <div className="mt-2 px-2">
                  <input
                    type="text"
                    placeholder="Add a comment (optional)"
                    value={currentComment}
                    onChange={(e) => handleCommentChange(id, e.target.value)}
                    disabled={!currentRating}
                    className="w-full p-2 border border-gray-300 rounded"
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
