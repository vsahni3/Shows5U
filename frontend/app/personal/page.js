"use client";

import { useState, useEffect } from "react";
import Header from "../components/Header";
import PreferenceCard from '../components/PreferenceCard';
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
            const sorted = data["results"].sort((a, b) => {
              if (a.comment && !b.comment) return -1;
              if (!a.comment && b.comment) return 1;
              return 0;
            });
            setPreferences(sorted);
      
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


   // Submit ratings and comments for a single item
   const handleSubmit = async (result, id, contentType) => {
    if (!result.rating) {
      alert("Please add a rating before submitting.");
      return;
    }

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/preference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // not adding seen for now
        body: JSON.stringify({ content_type: contentType, seen: result.seen, url: result.url, image_url: result.image_url, email: email, title: result.title, rating: result.rating, comment: result.comment }),
      });
      setPreferences(prev =>
        prev.map((item, idx) => idx === id ? result : item)
      );


    } catch (error) {
      console.error('Preference submission failed:', error);
    }

  };

  const handleDelete = async (result, id, contentType) => {
    if (!result.rating) {
      alert("Please add a rating before submitting.");
      return;
    }

    setPreferences(prev => prev.filter((_, i) => i !== id));


    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/preference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // not adding seen for now
        body: JSON.stringify({ content_type: contentType, seen: result.seen, url: result.url, image_url: result.image_url, email: email, title: result.title }),
      });


    } catch (error) {
      console.error('Preference submission failed:', error);
    }

  };
  const preferredOrder = ["anime", "series", "movie"];

  const sortedContentTypes = Object.keys(groupedPreferences).sort(
    (a, b) => preferredOrder.indexOf(a) - preferredOrder.indexOf(b)
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onSignOut={() => {}} isLoading={false} />
      <div className="pt-20 mt-10 px-4 sm:px-8 lg:px-60 space-y-12">
        {/* Loop over each content type (anime, movie, series, etc.) */}
        {sortedContentTypes.map((contentType) => {
          const items = groupedPreferences[contentType];

          // Skip if no items
          if (!items || items.length === 0) return null;

          return (
            <div key={contentType}>
              {/* Section heading */}
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-6 
               capitalize break-words w-full text-center sm:text-left">
                {contentType}
              </h2>

              {/* Cards grid */}
              <div className="grid gap-6 grid-cols-[repeat(auto-fit,200px)] justify-center sm:justify-start">

                {items.map((result, index) => {

                  if (
                    !result.image_url ||
                    !result.image_url.startsWith("http") ||
                    !result.title
                  ) {
                    return null;
                  }

                  return <PreferenceCard key={index} result={result} mode="view" onSave={(result) => handleSubmit(result, index, contentType)} onDelete={(result) => handleDelete(result, index, contentType)} />
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