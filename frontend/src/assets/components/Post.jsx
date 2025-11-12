import { useState, useEffect } from "react";
import { Heart, MessageCircle, Clock } from "lucide-react";
import { likePost, unlikePost } from "../services/api";
import WorkoutSummary from "./WorkoutSummary";

const Post = ({ post, currentUserId }) => {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(post.like_count ?? 0);

  useEffect(() => {
    if (Array.isArray(post.liked_by) && currentUserId) {
      setLiked(post.liked_by.includes(currentUserId));
    }
  }, [post.liked_by, currentUserId]);

  const handleLike = async () => {
    try {
      if (!liked) {
        setLiked(true);
        setLikeCount((prev) => prev + 1);
        await likePost(post.id);
      } else {
        setLiked(false);
        setLikeCount((prev) => (prev > 0 ? prev - 1 : 0));
        await unlikePost(post.id);
      }
    } catch (err) {
      console.error("Error toggling like:", err);
    }
  };


  return (
    <article className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6 transition hover:shadow-md w-full max-w-xl">
      <header className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">{post.title || "Untitled Post"}</h3>
          <p className="text-sm text-gray-500">@{post.username}</p>
        </div>
        {post.created_at && (
          <div className="flex items-center text-xs text-gray-400 gap-1">
            <Clock className="w-3 h-3" />
            {new Date(post.created_at).toLocaleDateString()}
          </div>
        )}
      </header>

      <div className="text-gray-700 leading-relaxed whitespace-pre-wrap mb-4">
        {post.content}
      </div>

      {/* Render WorkoutSummary if workout data exists */}
      {post.workout_data && (
        <WorkoutSummary workoutData={post.workout_data} />
      )}

      <footer className="flex items-center justify-between text-sm text-gray-600 border-t border-gray-100 pt-3">
        <div className="flex gap-4">
          <button
            onClick={handleLike}
            className="flex items-center gap-2 transition active:scale-95"
          >
            <Heart
              className={`w-5 h-5 ${liked ? "text-red-500 fill-red-500" : "text-red-500"}`}
            />
            <span>{likeCount}</span>
          </button>

          <button className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-blue-500" />
            <span>{post.comments?.length ?? 0}</span>
          </button>
        </div>
      </footer>
    </article>
  );
};

export default Post;
