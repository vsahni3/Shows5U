"use client";

import Header from "../components/Header";
import Link from "next/link";
import { useData } from '../context/dataContext';

const ResultsPage = () => {
  const { sharedData } = useData();

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onSignOut={() => {}} isLoading={false} />
      <div className="pt-20 mt-10 px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {sharedData.map((result, index) => (
            <Link key={index} href={result.url} target="_blank" rel="noopener noreferrer">
              <div className="bg-white shadow-md rounded-lg overflow-hidden cursor-pointer hover:shadow-lg transition">
                <img
                  src={result.image_url}
                  alt={result.title}
                  className="w-64 h-80 object-cover"
                />
                <div className="p-4">
                  <h2 className="text-lg font-semibold text-gray-800">{result.title}</h2>
                  <p className="text-sm text-gray-600">Genres: {result.genres.join(", ")}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;