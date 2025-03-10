'use client';

import { useState } from 'react';
import Head from 'next/head';
import { Card, Flex, Heading, Button } from '@radix-ui/themes';
import { useRouter } from 'next/navigation';
import { useData } from './context/dataContext';
import Header from './components/Header';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contentType, setContentType] = useState('anime'); // "anime", "movie", "series"
  const router = useRouter();
  const { setSharedData } = useData();

  // Handle search submit
  const handleSearchSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await fetch('http://127.0.0.1:5000/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, content_type: contentType }),
      });

      const data = await response.json();
      setSharedData(data['results']);
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
        <Flex
          direction="column"
          align="center"
          justify="center"
          className="flex-1 w-full mt-32 px-4"
        >
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
            {["anime", "movie", "series"].map((type) => (
              <button
                key={type}
                onClick={() => setContentType(type)}
                className={`py-2 px-6 rounded-full font-medium transition-all duration-200
                  ${
                    contentType === type
                      ? "bg-blue-500 text-white shadow-md"
                      : "text-gray-600 hover:bg-gray-200"
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
              placeholder={`Enter ${contentType == 'anime' ? 'an' : 'a'} ${contentType} query...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search"
              className="w-full bg-transparent text-gray-900 outline-none text-lg px-4 placeholder-gray-400"
            />
            <Button
              type="submit"
              variant="solid"
              className="px-6 py-3 text-white text-lg font-semibold rounded-full transition-all bg-blue-600 hover:bg-blue-700 shadow-md"
            >
              Search
            </Button>
          </form>
        </Flex>

        {/* Trending Section */}
        <div className="max-w-[1400px] mx-auto px-4 mt-20 mb-16">
          <Heading
            as="h2"
            size="5"
            className="text-center text-gray-800 font-semibold text-2xl mb-8"
          >
            Trending {contentType.charAt(0).toUpperCase() + contentType.slice(1)}
          </Heading>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5">
            {Array.from({ length: 12 }).map((_, index) => (
              <Card
                key={index}
                className="w-full h-80 rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition-all bg-white border border-neutral-200"
              >
                <img
                  src={
                    contentType === "anime"
                      ? "/luffy.png"
                      : contentType === "movie"
                      ? "/luffy.png"
                      : "/luffy.png"
                  }
                  alt={`${contentType.charAt(0).toUpperCase() + contentType.slice(1)} ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </Card>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
