'use client';

import { useState } from 'react';
import Head from 'next/head';
import { Card, Flex, Heading, Button } from '@radix-ui/themes';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  // Handle search submit
  const handleSearchSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, content_type: "anime" }),
      });

      if (!response.ok) throw new Error('Failed to fetch results');

      const data = await response.json();

      // Navigate to the results page with search results
      router.push(`/results?data=${encodeURIComponent(JSON.stringify(data))}`);
    } catch (error) {
        console.error('Search failed:', error);
    } finally {
        setIsLoading(false); // End loading state
    }
  };

  // Handle sign out
  const handleSignOut = () => {
    console.log('Sign Out clicked');
  };

  return (
    <>
      <Head>
        <title>Anime Search</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Full Page Layout */}
      <div className="min-h-screen flex flex-col bg-neutral-50 text-gray-800">
        {/* Fixed Navbar */}
        <Flex
          justify="between"
          align="center"
          className="bg-white w-full px-8 py-3 fixed top-0 left-0 right-0 shadow-sm z-10"
        >
      
  {/* Logo and Nav Links */}
  <Flex align="center" gap="4">
    <img
      src="/luffy.png"
      alt="Logo"
      className="w-16 h-16 object-contain object-cover rounded-full"
    />
    <Heading
      size="4"
      className="text-gray-700 font-medium"
    >
      Shows5U
    </Heading>
    <Heading
      size="4"
      className="text-gray-700 font-medium"
    >
      Personal
    </Heading>
  </Flex>

  {/* Sign Out Button */}
  <Button
    onClick={handleSignOut}
    variant="soft"
    className="px-4 py-2 text-sm rounded-md bg-neutral-100 hover:bg-neutral-200 transition-colors"
  >
    Sign Out
  </Button>
</Flex>

        {/* Central Search Section */}
        <Flex
          direction="column"
          align="center"
          justify="center"
          className="flex-1 w-full mt-48 px-4"
        >
          <Heading
            as="h1"
            size="6"
            className="mb-10 text-center text-gray-700 text-4xl font-light tracking-tight"
          >
            Search for Anime
          </Heading>
          <form 
            onSubmit={handleSearchSubmit} 
            className="w-full max-w-2xl flex items-center bg-white rounded-full shadow-md px-5 py-3 transition focus-within:shadow-lg"
          >
            <input
              type="text"
              name="anime"
              placeholder="Enter an anime title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search Anime"
              className="w-full bg-transparent text-gray-900 outline-none text-lg px-4"
            />
            <Button
              type="submit"
              variant="solid"
              className="px-6 py-2 bg-blue-600 text-white text-base rounded-full hover:bg-blue-700 transition-colors"
            >
              Search
            </Button>
          </form>
        </Flex>

        {/* Trending Anime Section */}
        <div className="max-w-[1400px] mx-auto px-4 mt-20 mb-16">
          <Heading
            as="h2"
            size="5"
            className="text-center text-gray-700 font-semibold text-2xl mb-8"
          >
            Trending Now
          </Heading>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5">
            {Array.from({ length: 12 }).map((_, index) => (
              <Card
                key={index}
                className="w-full h-80 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow bg-white border border-neutral-200"
              >
                <img
                  src="/luffy.png"
                  alt={`Anime ${index + 1}`}
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
