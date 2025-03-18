'use client';

import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';
import { Flex, Heading, Button } from '@radix-ui/themes';
import { useRouter } from 'next/navigation';
import { useData } from './context/dataContext';
import Header from './components/Header';
import { createClient } from '@/app/utils/supabase/client';

interface TrendingResult {
  title: string;
  image_url: string;
  url: string;
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [cachedTrendingResults, setCachedTrendingResults] = useState<{
    anime?: TrendingResult[];
    movie?: TrendingResult[];
    series?: TrendingResult[];
  }>({});
  const [contentType, setContentType] = useState<'anime' | 'movie' | 'series'>('anime');
  const router = useRouter();
  const [email, setEmail] = useState<string>('');
  interface SharedData {
    trendingResults: {
      anime?: TrendingResult[];
      movie?: TrendingResult[];
      series?: TrendingResult[];
    };
  }
  
  const { sharedData, setSharedData } = useData() as { 
    sharedData: SharedData; 
    setSharedData: React.Dispatch<React.SetStateAction<SharedData>>; 
  };

  // Refs for trending result cards and state for uniform height.
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [maxHeight, setMaxHeight] = useState<number>(0);

  const trendingContent = cachedTrendingResults[contentType] || [];

  // Callback ref to capture each card's element and calculate uniform height.
  const setCardRef = (el: HTMLDivElement | null, index: number): void => {
    cardRefs.current[index] = el;
    if (cardRefs.current.filter((ref) => ref !== null).length === trendingContent.length) {
      const heights = cardRefs.current
        .filter((ref): ref is HTMLDivElement => ref !== null)
        .map((ref) => ref.clientHeight);
      const newMaxHeight = Math.max(...heights);
      if (newMaxHeight !== maxHeight) {
        setMaxHeight(newMaxHeight);
      }
    }
  };

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
    async function fetchTrending() {
      // 2 levels of cache
      if (cachedTrendingResults[contentType]) return;
      if (sharedData.trendingResults?.[contentType]) {
        setCachedTrendingResults((prevCache) => ({
          ...prevCache,
          [contentType]: sharedData.trendingResults[contentType],
        }));
        return; // Use cached results from shared data
      }

  
      try {
        console.log("fetching");
        const response = await fetch('http://127.0.0.1:5000/trending', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content_type: contentType }),
        });
        const data = await response.json();
  
        // Store results in cache
        setCachedTrendingResults((prevCache) => ({
          ...prevCache,
          [contentType]: data['results'],
        }));
        setSharedData((prev) => ({
          ...prev,
          trendingResults: { ...prev.trendingResults, [contentType]: data['results'] }
        }));
      } catch (error) {
        console.error('Fetching trending content failed:', error);
      }
    }
  
    fetchTrending();
  }, [contentType, cachedTrendingResults, sharedData.trendingResults, setSharedData]);

  // Handle search form submission.
  const handleSearchSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, content_type: contentType, email }),
      });
      const data = await response.json();
      localStorage.setItem('searchResults', JSON.stringify({
        results: data['results'],
        contentType,
      }));
      router.push('/results');
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <>
      <Head>
        <title>Anime Search</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Full Page Layout */}
      <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
        {/* Fixed Navbar */}
        <Header isLoading={isLoading} />

        {/* Central Search Section */}
        <Flex direction="column" align="center" justify="center" className="flex-1 w-full mt-32 px-4">
          {/* Title */}
          <Heading
            as="h1"
            size="6"
            className="mb-6 text-center text-gray-900 text-5xl font-semibold tracking-tight"
          >
            Search {contentType.charAt(0).toUpperCase() + contentType.slice(1)}
          </Heading>

          {/* Selection Buttons */}
          <div className="mb-8 flex gap-1 bg-gray-100 p-1 rounded-full shadow-inner">
            {(['anime', 'movie', 'series'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setContentType(type)}
                className={`py-2 px-6 rounded-full font-medium transition-all duration-200 ${
                  contentType === type
                    ? 'bg-blue-500 text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>

          {/* Search Bar */}
          <form
  
            onSubmit={handleSearchSubmit}
            className="w-full max-w-2xl flex items-center bg-white rounded-full shadow-lg px-6 py-4 focus-within:shadow-2xl"
          >
            <input
              type="text"
              name="search"
              placeholder={`Enter ${contentType === 'anime' ? 'an' : 'a'} ${contentType} query...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search"
              className="w-full bg-transparent text-gray-900 outline-none text-lg px-4 placeholder-gray-400"
            />
            <Button
              disabled={isLoading}
              type="submit"
              variant="solid"
              className="px-6 py-3 text-white text-lg font-semibold rounded-full transition-all bg-blue-600 hover:bg-blue-700 shadow-md"
            >
              {isLoading ? "Loading..." : "Search"}
            </Button>
          </form>
        </Flex>

        {/* Trending Section */}
        <div className="max-w-[1400px] mx-auto px-4 mt-10 mb-16">
          <Heading as="h2" size="5" className="text-center text-gray-800 font-semibold text-2xl mb-8">
            Trending {contentType.charAt(0).toUpperCase() + contentType.slice(1)}
          </Heading>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5">
            {trendingContent.length > 0 ? (
              trendingContent.map((result, index) => (
                <Link key={index} href={result.url} target="_blank" rel="noopener noreferrer">
                  <div
                    ref={(el) => setCardRef(el, index)}
                    className="bg-white shadow-md rounded-lg overflow-hidden cursor-pointer hover:shadow-lg transition flex flex-col"
                    style={{ height: maxHeight ? maxHeight : 'auto' }}
                  >
                    <div className="relative w-full h-80">
                    <Image
                      src={result.image_url}
                      alt={result.title}
                      className="object-cover"
                      loading="lazy"
                      fill
                    />
                    </div>
                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <h2 className="text-lg font-semibold text-gray-800 line-clamp-2 overflow-hidden">
                        {result.title}
                      </h2>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <p className="text-center text-gray-600">No trending results available.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
