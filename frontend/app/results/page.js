"use client";

import Header from "../components/Header";
import Link from "next/link";
import Image from "next/image";
import { useState, useEffect } from "react";
import { createClient } from '@/app/utils/supabase/client';

const ResultsPage = () => {
  const [results, setResults] = useState([]);
  const [contentType, setContentType] = useState('');


  // Global state to hold ratings and comments
  const [ratingsData, setRatingsData] = useState({});
  const [email, setEmail] = useState('');



  useEffect(() => {
    const storedData = localStorage.getItem('searchResults');
    if (storedData) {
      const parsedData = JSON.parse(storedData);
      setResults(parsedData.results || []);
      setContentType(parsedData.contentType || '');
    }
  }, []);

  useEffect(() => {
      const supabase = createClient();
      async function fetchUserEmail() {
        const {
          data: { user },
        } = await supabase.auth.getUser();
        if (user) {
          setEmail(user.email || '');
        }
      }
      fetchUserEmail();
    }, []);

  // StarRating component with toggle behavior
  const StarRating = ({ id, rating, onRatingChange }) => {
    return (
      <div className="flex justify-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`cursor-pointer text-1xl ${star <= rating ? "text-yellow-500" : "text-gray-400"}`}
            onClick={() => onRatingChange(id, rating === star ? 0 : star)}
          >
            {star <= rating ? "★" : "☆"}
          </span>
        ))}
      </div>
    );
  };


  
  const renderSeenBadge = (seen, onToggle) => {
    return (
      <div
        onClick={(e) => { 
          e.stopPropagation(); // Prevents event bubbling if inside a link
          e.preventDefault();  // Prevents accidental link click
          onToggle();
        }}
        className={`absolute top-2 left-2 text-white text-xs font-bold px-2 py-1 rounded cursor-pointer ${
          seen ? "bg-green-500" : "bg-red-500"
        } hover:opacity-90 transition`}
      >
        {seen ? "Seen" : "Not Seen"}
      </div>
    );
  };

  // Handle star rating change
  const handleRatingChange = (id, rating) => {
    setRatingsData((prev) => ({
      ...prev,
      [id]: { ...prev[id], rating },
    }));
  };

  // Handle comment change
  const handleCommentChange = (id, comment) => {
    setRatingsData((prev) => ({
      ...prev,
      [id]: { ...prev[id], comment },
    }));
  };

  const toggleSeen = (id) => {
    setRatingsData((prev) => ({
      ...prev,
      [id]: { ...prev[id], seen: !(prev[id]?.seen ?? false) },
    }));
  };

  // Submit ratings and comments for a single item
  const handleSubmit = async (id) => {
    const entry = ratingsData[id];
    if (!entry || !entry.rating) {
      alert("Please add a rating before submitting.");
      return;
    }

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/preference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // not adding seen for now
        body: JSON.stringify({ content_type: contentType, seen: entry.seen, genres: results[id].genres.join(', '), description: results[id].description, url: results[id].url, image_url: results[id].image_url, email: email, title: results[id].title, rating: entry.rating, comment: entry.comment }),
      });


    } catch (error) {
      console.error('Preference submission failed:', error);
    }
    handleRatingChange(id, 0);
    handleCommentChange(id, "");
  };



  if (!results || results.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Header onSignOut={() => {}} isLoading={false} />
        <p className="text-gray-600 text-xl">No results found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onSignOut={() => {}} isLoading={false} />
      <div className="pt-20 mt-10 px-40">
      <div className="grid gap-6 grid-cols-[repeat(auto-fit,200px)] justify-left">

          {results.map((result, index) => {
            const id = result.id || index.toString();

            if (!result.image_url || !result.title || !result.image_url.startsWith("http")) return null;

            const currentRating = ratingsData[id]?.rating || 0;
            const currentComment = ratingsData[id]?.comment || "";
            const currentSeen = ratingsData[id]?.seen ?? false;

            return (
              <div key={id} className="flex flex-col bg-white shadow-md rounded-lg overflow-hidden">
                <Link href={result.url} target="_blank" rel="noopener noreferrer">
                  <div className="relative w-full" style={{ paddingTop: "150%" }}>
                  <div className="absolute top-0 left-0 w-full h-full">
                    <Image
                      src={result.image_url}
                      alt={result.title}
                      className="object-cover"
                      loading="lazy"
                      fill
                    />
                    </div>
                   
                   {renderSeenBadge(currentSeen, () => toggleSeen(id))}
                
                  </div>
                  <div className="p-2">
                  <h2 className="text-lg font-semibold text-gray-800 line-clamp-2 overflow-hidden min-h-[3em]">
                      {result.title}

                    </h2>
                    <p className="text-sm text-blue-600 italic">
                      Confidence: {result.score ? `${result.score.toFixed(2)}%` : "N/A"}
                    </p>
                  </div>
                </Link>

                {/* Star Rating */}
                <div>
                  <StarRating id={id} rating={currentRating} onRatingChange={handleRatingChange} />
                </div>
                {/* Comment Input */}
                <div className="mt-1 flex justify-center">
                  <input
                    type="text"
                    placeholder="Add a comment (optional)"
                    value={currentComment}
                    onChange={(e) => handleCommentChange(id, e.target.value)}
                    className="w-full max-w-[90%] h-8 p-1 border border-gray-300 rounded text-sm text-center" // Ensuring it stays centered
                  />
                </div>

                {/* Submit Button */}
                <div className="mt-1 py-2 flex justify-center">
                  <button
                    onClick={() => handleSubmit(id)}
                    className="px-3 py-1 text-sm text-white bg-blue-500 hover:bg-blue-600 rounded-md transition-all"
                  >
                    Submit
                  </button>
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
