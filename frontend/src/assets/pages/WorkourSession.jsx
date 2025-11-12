import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import Header from "../components/Header";
import { createWorkoutSession, createPost } from "../services/api";

const WorkoutSession = ({ username, setIsAuthed, setUsername }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const plan = location.state?.selectedPlan;

  const [formData, setFormData] = useState(() =>
    plan?.exercises.map((ex) => ({
      name: ex.name,
      sets: Array.from({ length: ex.sets }, () => ({ weight: "", reps: "" })),
    })) || []
  );

  const handleChange = (exerciseIndex, setIndex, field, value) => {
    setFormData((prev) => {
      const updated = [...prev];
      updated[exerciseIndex].sets[setIndex][field] = value;
      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const payload = {
        // ✅ only send date (YYYY-MM-DD)
        session_date: new Date().toISOString().split("T")[0],
        notes: `Workout for plan: ${plan.plan_name}`,
        workoutPlan: {
          name: plan.plan_name,
          description: plan.description || "",
          exercises: formData.map((ex) => {
            // compute averages or totals for all sets
            const totalWeight = ex.sets.reduce(
              (acc, s) => acc + parseFloat(s.weight || 0),
              0
            );
            const totalReps = ex.sets.reduce(
              (acc, s) => acc + parseInt(s.reps || 0),
              0
            );
            const avgWeight =
              ex.sets.length > 0 ? totalWeight / ex.sets.length : 0;
            const avgReps = ex.sets.length > 0 ? totalReps / ex.sets.length : 0;

            return {
              name: ex.name,
              type: "strength", // or cardio, etc.
              sets: ex.sets.length,
              reps: avgReps,
              exercise_weight: avgWeight,
            };
          }),
        },
      };

      // Create workout session
      await createWorkoutSession(payload);

      // Automatically create a post with the workout summary
      const postPayload = {
        title: `Completed: ${plan.plan_name}`,
        content: `Just finished my workout! 💪`,
        workout_data: payload.workoutPlan,
      };
      
      await createPost(postPayload);

      alert("Workout session logged and shared successfully!");
      navigate("/");
    } catch (err) {
      console.error("Failed to submit session:", err);
      alert("Failed to log workout session");
    }
  };

  if (!plan)
    return <p className="text-center mt-8 text-red-500">No workout plan selected.</p>;

  return (
    <div className="min-h-screen bg-gray-50">
        <Header 
            username={username}
            setIsAuthed={setIsAuthed}
            setUsername={setUsername} 
        />
      <div className="max-w-3xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-6 text-center">{plan.plan_name}</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {formData.map((exercise, exIndex) => (
            <div key={exIndex} className="border rounded-xl p-4 bg-white shadow">
              <h2 className="text-xl font-semibold mb-2">{exercise.name}</h2>
              {exercise.sets.map((set, setIndex) => (
                <div key={setIndex} className="flex gap-3 mb-2">
                  <span className="w-12 font-medium">Set {setIndex + 1}</span>
                  <input
                    type="number"
                    placeholder="Weight"
                    value={set.weight}
                    onChange={(e) =>
                      handleChange(exIndex, setIndex, "weight", e.target.value)
                    }
                    className="border p-2 rounded w-24"
                  />
                  <input
                    type="number"
                    placeholder="Reps"
                    value={set.reps}
                    onChange={(e) =>
                      handleChange(exIndex, setIndex, "reps", e.target.value)
                    }
                    className="border p-2 rounded w-24"
                  />
                </div>
              ))}
            </div>
          ))}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Complete Workout
          </button>
        </form>
      </div>
    </div>
  );
};

export default WorkoutSession;
