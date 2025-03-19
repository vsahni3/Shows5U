"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";

// StarRating component that supports view/edit
const StarRating = ({ rating, onRatingChange, editable }) => {
  return (
    <div className="flex justify-center">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`cursor-${editable ? "pointer" : "default"} text-1xl ${
            star <= rating ? "text-yellow-500" : "text-gray-400"
          }`}
          onClick={editable ? () => onRatingChange(rating === star ? 0 : star) : undefined}
        >
          {star <= rating ? "★" : "☆"}
        </span>
      ))}
    </div>
  );
};

const PreferenceCard = ({
  result,
  mode = "view", // 'view' or 'edit'
  onSave: externalSave,
  onDelete: externalDelete,
}) => {
  const editMode = mode == "edit";
  const [editing, setEditing] = useState(editMode);
  const [clickedEdit, setClickedEdit] = useState(false);
  const [localRating, setLocalRating] = useState(result.rating || 0);
  const [localComment, setLocalComment] = useState(result.comment || "");

  

  const handleSave = () => {
    const updatedData = { ...result, rating: localRating, comment: localComment };
    if (externalSave) externalSave(updatedData);
    // keep edit mode if initially edit
    setEditing(editMode);
    if (editMode) {
        setLocalComment("");
        setLocalRating(0);
    }
  };

  const handleDelete = () => {
    if (externalDelete) externalDelete(result);
    setEditing(false);
  };


  return (
    <div className="relative flex flex-col bg-white shadow-md rounded-lg overflow-hidden">
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
          {/* Seen Badge */}
          {result.seen ? (
            <div className="absolute top-2 left-2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">
              Seen
            </div>
          ) : (
            <div className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
              Not Seen
            </div>
          )}
          {/* Edit button only in view mode */}
          {!editing && (
            <button
              className="absolute top-2 right-2 text-xs text-blue-500 hover:underline"
              onClick={(e) => {
                e.preventDefault();
                setEditing(true);
                setClickedEdit(true);
              }}
            >
              Edit
            </button>
          )}
        </div>
        <div className="p-2">
          <h2 className="text-lg font-semibold text-gray-800 line-clamp-2 overflow-hidden min-h-[3em]">
            {result.title}
          </h2>
          {/* Confidence Score */}
          {result.score && (
            <p className="text-sm text-blue-600 italic">
              Confidence: {result.score ? `${result.score.toFixed(2)}%` : "N/A"}
            </p>
          )}
        </div>
      </Link>

      {/* Editable Section */}
      {editing ? (
        <>
          <div>
            <StarRating rating={localRating} onRatingChange={setLocalRating} editable />
          </div>
          <div className="mt-1 flex justify-center">
            <input
              type="text"
              value={localComment}
              onChange={(e) => setLocalComment(e.target.value)}
              className="w-full max-w-[90%] h-8 p-1 border border-gray-300 rounded text-sm text-center"
              placeholder="Add a comment (optional)"
            />
          </div>
          <div className="mt-1 py-2 flex justify-center space-x-2">
            <button
              onClick={handleSave}
              className="px-3 py-1 text-sm text-white bg-blue-500 hover:bg-blue-600 rounded-md transition-all"
            >
              Submit
            </button>
            {(editing && clickedEdit) && (
              <button
                onClick={handleDelete}
                className="px-3 py-1 text-sm text-white bg-red-500 hover:bg-red-600 rounded-md transition-all"
              >
                Delete
              </button>
            )}
          </div>
        </>
      ) : (
        <>
          {/* Static View */}
          <div>
            <StarRating rating={result.rating} onRatingChange={() => {}} editable={false} />
          </div>
          {result.comment && (
            <div className="mt-1 flex justify-center text-sm text-gray-600 italic">
              “{result.comment}”
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PreferenceCard;
