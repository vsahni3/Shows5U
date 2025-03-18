"use client";

import { useState, useEffect } from "react";
import Header from "../components/Header";
import Link from "next/link";
import Image from "next/image";
import { createClient } from '@/app/utils/supabase/client';

// Example: assume results is provided from context or props
// Each object in results should have: title, rating, content_type, comment, seen, url, img_url
// e.g., const results = [{ title: "My Anime", rating: 4, content_type: "anime", comment: "Loved it", seen: true, url: "https://...", img_url: "https://..." }, ...];

const PreferencesPage = () => {
  // Assume results is already available
  const [preferences, setPreferences] = useState([]);

  const [email, setEmail] = useState('');

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

  useEffect(() => {
    if (!email) return;

    async function fetchPreferences() {

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/personal`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              // not adding seen for now
              body: JSON.stringify({ email: email }),
            });
            const data = await response.json();
            setPreferences(data["results"]);
      
          } catch (error) {
            console.error('Preference submission failed:', error);
          } 
    }
    fetchPreferences();
  }, [email]);

  // Group preferences by content_type
  const groupedPreferences = preferences.reduce((acc, pref) => {
    if (!acc[pref.content_type]) {
      acc[pref.content_type] = [];
    }
    acc[pref.content_type].push(pref);
    return acc;
  }, {});

  // Fixed star rating (non-clickable)
  const renderStars = (rating) => {
    return (
      <div className="text-lg">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={star <= rating ? "text-yellow-500" : "text-gray-300"}>
            ★
          </span>
        ))}
      </div>
    );
  };

  // Creative seen indicator using a badge overlay on the card image
  const renderSeenBadge = (seen) => {
    return seen ? (
      <div className="absolute top-2 left-2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">
        Seen
      </div>
    ) : (
      <div className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
        Not Seen
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onSignOut={() => {}} isLoading={false} />
      <div className="pt-20 mt-10 px-60 space-y-12">
        {/* Loop over each content type (anime, movie, series, etc.) */}
        {Object.keys(groupedPreferences).map((contentType) => {
          const items = groupedPreferences[contentType];

          // Skip if no items
          if (!items || items.length === 0) return null;

          return (
            <div key={contentType}>
              {/* Section heading */}
              <h2 className="text-3xl font-bold text-gray-800 mb-6 capitalize">
                {contentType}
              </h2>

              {/* Cards grid */}
              <div className="grid gap-6 grid-cols-[repeat(auto-fit,200px)] justify-left">

                {items.map((result, index) => {
                  console.log(result)
                  if (
                    !result.image_url ||
                    !result.image_url.startsWith("http") ||
                    !result.title
                  ) {
                    return null;
                  }

                  return (
                    <div
                      key={index}
                      className="flex flex-col bg-white shadow-md rounded-lg overflow-hidden"
                    >
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
                          {renderSeenBadge(result.seen)}
                        </div>
                        <div className="p-4">
                          <h3 className="text-lg font-semibold text-gray-800 line-clamp-2 overflow-hidden min-h-[3em]">
                            {result.title}
                          </h3>
                        </div>
                      </Link>

                      {/* Star rating */}
                      <div className="px-4 pb-4">{renderStars(result.rating)}</div>

                      {/* Comment (if available) */}
                      {result.comment && (
                        <div className="px-4 pb-4 text-sm text-gray-600 italic">
                          “{result.comment}”
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PreferencesPage;