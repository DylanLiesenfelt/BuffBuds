import { Dumbbell, TrendingUp } from "lucide-react";

const WorkoutSummary = ({ workoutData }) => {
  if (!workoutData || !workoutData.exercises) {
    return null;
  }

  const { name, description, exercises } = workoutData;
  
  // Calculate total volume across all exercises
  const totalVolume = exercises.reduce((sum, ex) => {
    return sum + (ex.sets * ex.reps * ex.exercise_weight);
  }, 0);

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200 mb-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <Dumbbell className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold text-gray-800">{name}</h3>
      </div>

      {/* Description */}
      {description && (
        <p className="text-sm text-gray-600 mb-3">{description}</p>
      )}

      {/* Exercises List */}
      <div className="space-y-2 mb-3">
        {exercises.map((exercise, idx) => (
          <div 
            key={idx} 
            className="bg-white rounded-lg p-3 shadow-sm border border-gray-100"
          >
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-semibold text-gray-800">{exercise.name}</h4>
                <p className="text-xs text-gray-500 capitalize">{exercise.type}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-700">
                  {exercise.sets} × {exercise.reps} reps
                </p>
                <p className="text-xs text-gray-500">
                  {exercise.exercise_weight.toFixed(1)} lbs
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Total Volume */}
      <div className="flex items-center gap-2 pt-3 border-t border-blue-200">
        <TrendingUp className="w-4 h-4 text-indigo-600" />
        <span className="text-sm font-semibold text-gray-700">
          Total Volume: <span className="text-indigo-600">{totalVolume.toLocaleString()} lbs</span>
        </span>
      </div>
    </div>
  );
};

export default WorkoutSummary;
