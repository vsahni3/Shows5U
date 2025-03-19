"use client";

import Header from "../components/Header";
import PreferenceCard from '../components/PreferenceCard';
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


  



  // Submit ratings and comments for a single item
  const handleSubmit = async (result) => {
    if (!result.rating) {
      alert("Please add a rating before submitting.");
      return;
    }

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/preference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // not adding seen for now
        body: JSON.stringify({ content_type: contentType, seen: result.seen, genres: result.genres.join(', '), description: result.description, url: result.url, image_url: result.image_url, email: email, title: result.title, rating: result.rating, comment: result.comment }),
      });


    } catch (error) {
      console.error('Preference submission failed:', error);
    }

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

            return <PreferenceCard key={id} result={result} mode="edit" onSave={handleSubmit} />
          })}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
